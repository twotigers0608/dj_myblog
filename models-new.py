#!/usr/bin/env python

from collections import Counter, OrderedDict
import os
import datetime
import jsonfield
import random
import re
import logging
# import threadlocalrequest
#from eventlog.models import log
import pytz

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
#from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
import django.dispatch
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.six.moves import filter
from django.utils import timezone
from django.contrib.postgres.fields.array import ArrayField


class ExtManager(models.Manager):
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except ObjectDoesNotExist:
            return None


@python_2_unicode_compatible
class Person(models.Model):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    idsid = models.CharField(max_length=16, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        select_on_save = True

    def display_name(self):
        if self.name:
            return self.name
        else:
            return self.email

    def email_name(self):
        if (self.name):
            return "%s <%s>" % (self.name, self.email)
        else:
            return self.email

    def link_to_user(self, user):
        self.name = user.profile.name()
        self.user = user

    def __str__(self):
        return self.display_name()


@python_2_unicode_compatible
class GitProject(models.Model):
    protocol = models.CharField("net protocol to clone with", max_length=16, null=True, blank=True)
    host = models.CharField("host location of git project", max_length=255, null=True, blank=True)
    project = models.CharField("git project", max_length=255, null=True, blank=True)

    def __str__(self):
        return self.protocol + "://" + self.host + '/' + self.project 


@python_2_unicode_compatible
class Domain(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class DomainOwner(models.Model):
    owner = models.ForeignKey(Person, on_delete=models.CASCADE)
    domain = models.ForeignKey(Domain, null=True, on_delete=models.CASCADE)
    prim = models.BooleanField(default=False)
    notify = models.BooleanField(default=True)

    def __str__(self):
        return self.owner.name


@python_2_unicode_compatible
class CoeContact(models.Model):
    user = models.ForeignKey(Person, on_delete=models.CASCADE)
    domain = models.ForeignKey(Domain, null=True, on_delete=models.CASCADE)
    prim = models.BooleanField(default=False)
    notify = models.BooleanField(default=True)

    def __str__(self):
        return self.user.name


class Branch(models.Model):
    repo = models.ForeignKey(GitProject, null=True, on_delete=models.SET_NULL)
    branch = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    latest_tag = models.CharField("most recent tag rebased to", 
                                  max_length=255, null=True, blank=True)
    is_trusted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.repo) + '-->' + self.branch


class KernelProduct(models.Model):
    name = models.CharField(max_length=255, unique=True)
    # release branch prefix
    relbrh_prefix = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return str(self.name)


@python_2_unicode_compatible
class KernelProductDomain(models.Model):
    kproduct = models.ForeignKey(KernelProduct, on_delete=models.CASCADE)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    release_branch = models.ForeignKey(Branch, null=True, blank=True, 
                                       on_delete=models.SET_NULL)
    allow_duplicate = models.BooleanField(default=False)

    class Meta:
        unique_together = (('kproduct', 'domain'),)

    def __str__(self):
        return "%s/%s" % (self.kproduct.name, self.domain.name)


@python_2_unicode_compatible
class Reviewer(models.Model):
    ROLE_REVIEWER = 1
    ROLE_GATEKEEPER = 2
    ROLE_ROBOT = 3
    RROLE_CHOICES = (
        (ROLE_REVIEWER, "Reviewer"),
        (ROLE_GATEKEEPER, "Gatekeeper"),
        (ROLE_ROBOT, "Robot")
    )
        
    user = models.ForeignKey(Person, on_delete=models.CASCADE)
    kpdomain = models.ForeignKey(KernelProductDomain, on_delete=models.CASCADE)
    role = models.IntegerField(choices=RROLE_CHOICES, 
                               default=ROLE_REVIEWER)

    def __str__(self):
            return "%s: %s: %s" % (self.kpdomain, self.get_role_display(), self.user.name)


# memo: only pull request can be abandoned, only pull request can
# be marked as verified, built okay. If a pull request is abandoned,
# all patches of all review sets are ignored. So don't abandon a pr
# until you really don't want to merge those patches. If you just want
# to amend some of the patches, re-submit the pr and start a new review
# set
# UC: user submit a pr A at rc-3, it is not approved yet. In rc-5, user
#     wants to update this pr, resubmit it again. Some fields of pr like
#     b_base, b_revision, b_branch might be changed, should we keep the
#     old data in the database e.g. in table PRReviewSet?
#
@python_2_unicode_compatible
class PullRequest(models.Model):
    STATE_EMPTY = 7
    STATE_IMPORT_ERR = 8
    STATE_READY = 0
    STATE_APPROVED = 1
    STATE_REJECTED = 2
    STATE_BYPASSED = 3
    STATE_MERGED = 4
    STATE_BYPASS_MERGED = 5
    STATE_ABANDONED = 6
    STATE_CHOICES = (
        ( STATE_EMPTY, "Empty" ),
        ( STATE_IMPORT_ERR, "Import Error" ),
        ( STATE_READY, "Ready" ),
        ( STATE_APPROVED, "Approved" ),
        ( STATE_REJECTED, "Rejected" ),
        ( STATE_BYPASSED, "Bypassed" ),
        ( STATE_MERGED, "Merged" ),
        ( STATE_BYPASS_MERGED, "Merged without Review" ),
        ( STATE_ABANDONED, "Abandoned" )
    )

    CLASS_PUBLIC = 1
    CLASS_CONFIDENTIAL = 2
    CLASS_SECRET = 3
    CLASS_CHOICES = (
        ( CLASS_PUBLIC, "Public" ),
        ( CLASS_CONFIDENTIAL, "Intel Confidential" ),
        ( CLASS_SECRET, "Intel Restricted Secret" ),
    )

    jira = models.CharField(max_length=64, primary_key=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    kpdomain = models.ForeignKey(KernelProductDomain, on_delete=models.CASCADE)
    classification = models.IntegerField(choices=CLASS_CHOICES, default=CLASS_PUBLIC)
    #FIXME: copy JIRA status here
    state = models.IntegerField(choices=STATE_CHOICES, default=STATE_READY)
    # next patch review set number
    latest_prset = models.IntegerField(default=1)
    owner = models.ForeignKey(Person, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now=True)
    updated_date = models.DateTimeField(auto_now=True)

    a_branch = models.CharField(max_length=255, null=False, blank=False)
    b_branch = models.CharField(max_length=255, null=False, blank=False)
    a_revision = models.CharField(max_length=64, null=False, blank=False)
    b_revision = models.CharField(max_length=64, null=False, blank=False)
    a_base = models.CharField(max_length=64, null=False, blank=False)
    b_base = models.CharField(max_length=64, null=False, blank=False)
    # Job created by Metronome to go through a pullrequest lifecycle
    pr_job = models.CharField(max_length=64, null=True, blank=True)
    # qd_job: quiltdiff job
    # jenkins job for generating quilt diff which is imported by quiltreview
    qd_job = models.IntegerField(null=True, blank=True)

    objects = ExtManager()

    def __str__(self):
        return self.jira


@python_2_unicode_compatible
class PRSet(models.Model):
    pullrequest = models.ForeignKey(PullRequest, on_delete=models.CASCADE, null=True)
    reviewset = models.IntegerField()
    subject = models.CharField(max_length=255, null=True, blank=True)
    classification = models.IntegerField(choices=PullRequest.CLASS_CHOICES,
                                         default=PullRequest.CLASS_PUBLIC)
    state = models.IntegerField(choices=PullRequest.STATE_CHOICES)
    created_date = models.DateTimeField(null=True, blank=True)

    a_branch = models.CharField(max_length=255, null=False, blank=False)
    b_branch = models.CharField(max_length=255, null=False, blank=False)
    a_revision = models.CharField(max_length=64, null=False, blank=False)
    b_revision = models.CharField(max_length=64, null=False, blank=False)
    a_base = models.CharField(max_length=64, null=False, blank=False)
    b_base = models.CharField(max_length=64, null=False, blank=False)
    pr_job = models.CharField(max_length=64, null=True, blank=True)
    qd_job = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = (('pullrequest', 'reviewset'),)


@python_2_unicode_compatible
class PRComment(models.Model):
    pullrequest = models.ForeignKey(PullRequest,
                                    on_delete=models.CASCADE, null=True)
    reviewset = models.IntegerField()
    author = models.ForeignKey(Person, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now=True)
    content = models.TextField()

    class Meta:
        unique_together = (('pullrequest', 'reviewset', 'author'),)

    def __str__(self):
        return self.content


@python_2_unicode_compatible
class PatchReview(models.Model):
    STATE_NEW = 0
    STATE_APPROVED = 1
    STATE_REJECTED = 2
    STATE_UNDER_REVIEW = 3
    STATE_ON_HOLD = 4
    STATE_MERGED = 5
    STATE_BYPASSED = 6
    STATE_BYPASS_MERGED = 7
    STATE_REWORKED = 8
    STATE_CHOICES = (
        ( STATE_NEW, "New" ),
        ( STATE_APPROVED, "Approved" ),
        ( STATE_REJECTED, "Rejected" ),
        ( STATE_BYPASSED, "Bypassed" ),
        ( STATE_UNDER_REVIEW, "Under Review" ),
        ( STATE_REWORKED, "Reworked" ),
        ( STATE_ON_HOLD, "On Hold" ),
        ( STATE_MERGED, "Merged" ),
        ( STATE_BYPASS_MERGED, "Merged without Review" ),
    )

    SUBSTA_NOSCORE = 0
    SUBSTA_PLUS1 = 1
    SUBSTA_MINUS1 = 2
    SUBSTA_BOTH = 3
    SUBSTA_CHOICES = (
        ( SUBSTA_NOSCORE, "" ),
        ( SUBSTA_PLUS1, "+1" ),
        ( SUBSTA_MINUS1, "-1" ),
        ( SUBSTA_BOTH, "+1 -1" ),
    )

    REVIEWTYPE_NEW = 1
    REVIEWTYPE_UPDATED = 2
    REVIEWTYPE_REMOVED = 3
    REVIEWTYPE_REFONLY = 4
    REVIEWTYPE_UPSTREAMED = 5
    REVIEWTYPE_CHOICES = (
        ( REVIEWTYPE_NEW, "New Patch" ),
        ( REVIEWTYPE_UPDATED, "Updated Patch" ),
        ( REVIEWTYPE_REMOVED, "Removed Patch" ),
        ( REVIEWTYPE_UPSTREAMED, "Upstreamed Patch" ),
        ( REVIEWTYPE_REFONLY, "Reference Patch" )
    )

    # this field of reference patch is null/blank
    pullrequest = models.ForeignKey(PullRequest, null=True, blank=True,
                                    on_delete=models.CASCADE)
    patch = models.ForeignKey(Patch, on_delete=models.CASCADE)

    created_date = models.DateTimeField(auto_now=True)
    updated_date = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(Person, null=True, on_delete=models.SET_NULL)
    # pullrequest sets array
    prsets = ArrayField(models.IntegerField(), null=True, blank=True)
    reviewtype = models.IntegerField(choices=REVIEWTYPE_CHOICES,
                                     default=REVIEWTYPE_UPDATED)
    state = models.IntegerField(choices=STATE_CHOICES, default=STATE_NEW)
    substa = models.IntegerField(choices=SUBSTA_CHOICES, default=SUBSTA_NOSCORE)
    latest_patchset = models.IntegerField(default=1)

    # fields for reference:
    # only for review type: updated patch
    a_ref = models.IntegerField(null=True, blank=True)

    def add_reviewsets(self, val):
        if self.reviewsets and (val not in self.reviewsets):
            self.reviewsets.append(val)
        else:
            self.reviewsets = [val]

    def __str__(self):
        return self.subject


@python_2_unicode_compatible
class PatchSet(models.Model):
    patchreview = models.ForeignKey(PatchReview, on_delete=models.CASCADE)
    patchset = models.IntegerField(default=1)
    patch = models.ForeignKey(Patch, on_delete=models.CASCADE)
    state = models.IntegerField(choices=PatchReview.STATE_CHOICES,
                                default=PatchReview.STATE_NEW)

    class Meta:
        unique_together = (('patchreview', 'patchset'),)

    def __str__(self):
        return "%d-%d" % (self.patchreview_id, self.patchset)


@python_2_unicode_compatible
class Patch(models.Model):
    # patch hash: hash(subject + commit msg + payload)
    hash = models.CharField(max_length=64, primary_key=True)
    payload = models.ForeignKey(Payload, on_delete=models.CASCADE)

    subject = models.CharField(max_length=255)
    commit_msg = models.TextField(null=True, blank=True)
    tags = models.TextField(null=True, blank=True)
    commit_id = models.CharField(max_length=64, null=True, blank=True)
    author = models.ForeignKey(Person, related_name='author', null=True,
                               on_delete=models.SET_NULL)
    author_date = models.DateTimeField(null=True, blank=True)
    committer = models.ForeignKey(Person, related_name='committer', null=True, on_delete=models.SET_NULL)
    commit_date = models.DateTimeField(null=True, blank=True)
    bugs = ArrayField(models.CharField(max_length=128), null=True, blank=True)

    def add_bugs(self, val):
        if self.bugs:
            if val not in self.bugs:
                self.bugs.append(val)
        else:
            self.bugs = [val]

    def __str__(self):
        return self.subject


@python_2_unicode_compatible
class Payload(models.Model):
    hash = models.CharField(max_length=64, primary_key=True)
    text = models.TextField(null=True, blank=True)
    files = models.TextField(null=True, blank=True)
    insert_size = models.IntegerField(default=0)
    delete_size = models.IntegerField(default=0)

    def __str__(self):
        return self.hash


@python_2_unicode_compatible
class PatchComment(models.Model):
    patchreview = models.ForeignKey(PatchReview,
                                    on_delete=models.CASCADE, null=True)
    patchset = models.IntegerField(default=1)
    author = models.ForeignKey(Person, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now=True)
    content = models.TextField()

    class Meta:
        unique_together = (('pullrequest', 'reviewset', 'author'),)

    def __str__(self):
        return self.content


@python_2_unicode_compatible
class VoteRecord(models.Model):
    REVIEW_NOSCORE = 0
    REVIEW_PLUS_1 = 1
    REVIEW_MINUS_1 = -1
    REVIEW_SCORE_CHOICES = (
        (REVIEW_NOSCORE, "0"),
        (REVIEW_PLUS_1, "+1"),
        (REVIEW_MINUS_1, "-1")
    )
    VERIFY_NOSCORE = 0
    VERIFY_PLUS_1 = 1
    VERIFY_MINUS_1 = -1
    VERIFY_SCORE_CHOICES = (
        (VERIFY_NOSCORE, "0"),
        (VERIFY_PLUS_1, "+1"),
        (VERIFY_MINUS_1, "-1")
    )

    patchreview = models.ForeignKey(PatchReview,
                                    on_delete=models.CASCADE, null=True)
    patchset = models.IntegerField()
    voter = models.ForeignKey(Person, on_delete=models.CASCADE)
    review_score = models.IntegerField(choices=REVIEW_SCORE_CHOICES, 
                                       default=REVIEW_NOSCORE)
    verify_score = models.IntegerField(choices=VERIFY_SCORE_CHOICES, 
                                       default=VERIFY_NOSCORE)

    class Meta:
        unique_together = (('patchreview', 'patchset', 'voter'),)

    def __str__(self):
        return "%d/%d: %d" % (self.patchreview_id, self.patchset, self.id)


#@python_2_unicode_compatible
#class TrackingTicket(models.Model):
#    patchreview = models.ForeignKey(PatchReview, on_delete=models.CASCADE)
#    patchset = models.IntegerField(default=1)
#    ticket_id = models.CharField(max_length=16, null=False)
#
#    def __str__(self):
#        return self.ticket_id
#      
#    INTEL_JIRA_URL_BASE = 'https://jira01.devtools.intel.com/browse/'
#    TICKET_URL_BASES = {
#        'PKT'  : INTEL_JIRA_URL_BASE,
#        'OAM'  : INTEL_JIRA_URL_BASE,
#        'OPKTT': INTEL_JIRA_URL_BASE,
#        'PKTPR': INTEL_JIRA_URL_BASE,
#    }
#    def get_ticket_url(self):
#        # tcg: the ticket category
#        tcg = self.ticket_id.split('-')[0]
#        return "%s%s" % (TICKET_URL_BASES[tcg], self.ticket_id)
#
#    def set_ticket_from_url(self, url):
#        tid = os.path.basename(url)
#        tcg = tid.split('-')[0]
#
#        if tcg not in TICKET_URL_BASES:
#            __log.error("invalid ticket: %s" % url)
#
#        self.ticket_id = tid

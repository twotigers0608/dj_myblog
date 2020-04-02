
function usage() {
    print(" usage: awk -F',' -f /path/to/osit-log-parser.awk  \\") > STDERR
    print("                  arg_prod=<devbkc|4.9bkc> \\") > STDERR
    print("                  arg_build=xx \\") > STDERR
    print("                  arg_dev=<joule|gp|icl> \\") > STDERR
    print("                  [arg_ttype=<tiny|basic|full>] \\") > STDERR
    print("                  [arg_otype=<csv|xml>] \\") > STDERR
    print("                  /path/to/osit-raw-result.csv\n") > STDERR
    print("   arguments:") > STDERR
    print("     arg_prod  - product name(devbkc, 4.9bkc)") > STDERR
    print("     arg_build - build number") > STDERR
    print("     arg_dev   - device type, e.g. joule, icl, gp") > STDERR
    print("     arg_otype - output file type, csv or xml. The default is xml") > STDERR
    print("     arg_ttype - OSIT test type(tiny, base, full)\n") > STDERR
    print("   e.g: awk -F',' -f ./osit-log-parser.awk \\") > STDERR
    print("                  arg_build=devbkc \\") > STDERR
    print("                  arg_build=4.12.0-rc1-176 \\") > STDERR
    print("                  arg_dev=joule \\") > STDERR
    print("                  arg_ttype=full \\") > STDERR
    print("                  /tmp/OSIT_osit-base-subset.csv\n") > STDERR
}


function get_category(ori_cat) {
    ori_cat = tolower(ori_cat)
    if (ori_cat ~ /^ddt[_-]/) {
        return CATEGORY_PREFIX"-ddt"
    } else if (ori_cat ~ /^osit[_-]/) {
        return CATEGORY_PREFIX"-ltp"
    }
}


function get_device_type(dev) {
    if (!dev) {
        usage()
        exit 2
    }

    dev = tolower(dev)
    if (dev ~ /joule/) {
        return "Joule"
    } else if (dev ~ /(bxt_gp|gp)/) {
        return "BXT_GP"
    } else if (dev ~ /icl/) {
        return "ICL"
    } else if (dev ~ /kbl/) {
        return "KBL"
    } else {
        printf("Error: invalid device type: %s\n", dev) > STDERR
        exit 2
    }
}


function get_testplan_id(product, ttype) {

    if (!product) {
        usage()
        exit 2
    }

    # default test type is "customized"
    if (!ttype)
        ttype = "custom"

    ttype = tolower(ttype)
    product = tolower(product)

    if (ttype ~ /(tiny|1)/) {
        ttype = "tiny"
    } else if (ttype ~ /(base|basic|2)/) {
        ttype = "basic"
    } else if (ttype ~ /(full|3)/) {
        ttype = "full"
    } else if (ttype ~ /(custom|4)/) {
        ttype = "custom"
    } else {
        printf("Error: invalid test type: %s\n", ttype) > STDERR
        exit 2
    }

    if (product !~ /(devbkc|4.9bkc|4.14bkc)/) {
        printf("Error: invalid product: %s\n", product) > STDERR
        exit 2
    }
    key = product""SUBSEP""ttype
    if (key in TEST_PLAN_IDS) {
        return TEST_PLAN_IDS[key]
    } else {
        printf("Error: no test plan found for %s %s\n", product, ttype) > STDERR
        exit 2
    }
}


BEGIN {
    STDERR = "/dev/stderr"
    CATEGORY_PREFIX = "osit"

    # map osit test result number to lava test result
    # osit test result no.: 1: idle, 2: pass, 3: fail, 6: blocked
    # lava test result: pass, fail, skip
    TEST_RESULT_MAP[1] = "skip"
    TEST_RESULT_MAP[2] = "pass"
    TEST_RESULT_MAP[3] = "fail"
    TEST_RESULT_MAP[6] = "skip"

    TEST_PLAN_IDS["devbkc", "tiny"]   = "3"  # OSIT LBT tiny for devbkc
    TEST_PLAN_IDS["devbkc", "basic"]  = "4"  # OSIT LBT basic for devbkc
    TEST_PLAN_IDS["devbkc", "full"]   = "5"  # OSIT LBT full for devbkc
    TEST_PLAN_IDS["devbkc", "custom"] = "6"  # OSIT LBT custimized for devbkc
    TEST_PLAN_IDS["4.9bkc", "full"]   = "8"  # OSIT LBT full for 4.9bkc
    TEST_PLAN_IDS["4.9bkc", "tiny"]   = "13" # OSIT LBT tiny for 4.9bkc
    TEST_PLAN_IDS["4.14bkc", "full"]   = "8"  # OSIT LBT full for 4.14bkc
    TEST_PLAN_IDS["4.14bkc", "tiny"]   = "13" # OSIT LBT tiny for 4.14bkc

    SUITE_VERSION = "1"
    MANAGER = "dave.lin@intel.com"
    DEFAULT_TESTER = "dave.lin@intel.com"
    AUTHOR = "dave.lin@intel.com"
    TC_DEFAULT_STATUS = "2" # 2: confirmed
    TC_DEFAULT_PRIORITY = "3"
    RERUN_DEFAULT = "true"

    tc_count = 0
    # tc_cats
    # tc_names
    # tc_results
}

{
    # skip the header line or blank line
    if (NF < 6 || $0 ~ /Feature,Test_ID,/)
        next

    tc_cats[tc_count] = get_category($1)
    tc_names[tc_count] = tolower($2)

    # test result values:
    #  1: IDLE
    #  2: PASSED (default)
    #  3: FAILED
    #  4: RUNNING
    #  5: PAUSED
    #  6: BLOCKED
    #  7: ERROR
    result_str = tolower($3)
    result = "1"
    # The fourth field is "1" if it passes
    # The fifth field is "1" if it fails
    if (result_str == "passed") {
        result = "2"
    } else if (result_str == "failed") {
        result = "3"
    } else if (result_str == "blocked") {
        result = "6"
    }
    tc_results[tc_count] = result
    tc_count++
}

#<test_run name="" plan_id="" build_name="" env="" suite_version="" manager="" rerun_flag="" >
#  <tc_common_properties author="" default_tester="" status="" />
#  <test_case name="testcase1" priority="3" category="c1" result="2" >
#    <action></action>
#    <error></error>
#  </test_case>
#</test_run>
END {
    if (arg_otype == "csv") {
        for (i=0; i<tc_count; i++) {
            printf("%s,%s\n", tc_names[i], TEST_RESULT_MAP[tc_results[i]])
        }
        exit
    }

    gsub(/-/, "", arg_prod)
    tp_id = get_testplan_id(arg_prod, arg_ttype)
    dev_type = get_device_type(arg_dev)
    # testrun name: TEST_PLAN_ID"-"arg_build"-"arg_dev
    printf("<test_run name=\"%s-%s-%s\" plan_id=\"%s\" build_name=\"%s\" env=\"%s\" suite_version=\"%s\" manager=\"%s\" rerun_flag=\"%s\" >\n", 
              tp_id, arg_build, dev_type,
              tp_id,
              arg_build,
              dev_type,
              SUITE_VERSION,
              MANAGER,
              RERUN_DEFAULT)
    printf("  <tc_common_properties author=\"%s\" default_tester=\"%s\" status=\"%s\" />\n", 
             AUTHOR,
             DEFAULT_TESTER,
             TC_DEFAULT_STATUS)
    for (i=0; i<tc_count; i++) {
        printf("  <test_case name=\"%s\" priority=\"%s\" category=\"%s\" result=\"%s\" >\n",
                  tc_names[i],
                  TC_DEFAULT_PRIORITY,
                  tc_cats[i],
                  tc_results[i])
        printf("    <action></action>\n")
        #FIXME: check if there is any error in kmsg log
        printf("    <error></error>\n")
        printf("  </test_case>\n")
    }
    printf("</test_run>\n")
}

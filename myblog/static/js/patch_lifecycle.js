// Generated by CoffeeScript 1.9.3
(function() {
  var indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  angular.module('app').controller('patch_lifecycleController', function($state, $scope, metricsService, config, $timeout) {
    var graphCfg;
    graphCfg = $state.current.data;
    $scope.loading = true;
    $scope.viewsBooleans = {
      showcactusbranches: false,
      showgitbranches: false,
      showdomains: false,
      showweeks: true,
      showplatform: false,
      showtypes: false,
      showpriorities: false,
      showcomponents: false
    };
    $scope.switchView = function(selected_view_boolean) {
      var data_field, label, nb_remove, viewBoolean;
      for (viewBoolean in $scope.viewsBooleans) {
        $scope.viewsBooleans[viewBoolean] = false;
      }
      $scope.viewsBooleans[selected_view_boolean] = true;
      label = '';
      data_field = '';
      switch (selected_view_boolean) {
        case 'showcactusbranches':
          label = 'Cactus Branch';
          data_field = 'Builder';
          break;
        case 'showgitbranches':
          label = 'Git Branch';
          data_field = 'Branch';
          break;
        case 'showdomains':
          label = 'Patch Domain';
          data_field = 'Domain';
          break;
        case 'showplatform':
          label = 'Program/Platform';
          data_field = 'BugPlatform';
          break;
        case 'showtypes':
          label = 'Bug Type';
          data_field = 'BugType';
          break;
        case 'showcomponents':
          label = 'Bug Component';
          data_field = 'ComponentName';
          break;
        case 'showpriorities':
          label = 'Bug Priority';
          data_field = 'BugPriority';
      }
      nb_remove = $scope.db.columns().length === $scope.nb_columns_original ? 0 : 1;
      if (label !== '') {
        $scope.db.columns().splice(2, nb_remove, {
          label: label,
          format: function(d) {
            return d[data_field];
          }
        });
      }
      return $scope.db.redraw();
    };
    return metricsService.jsv(graphCfg.api_url).then(function(data) {
      var all, create_attr_dimension, dataCountChart, implement_link, ndx, reduce_add, reduce_del, reduce_init, remove_empty_bins, usableData, x;
      if (data.length === 0) {
        $scope.nodata = true;
        return;
      }
      $scope.loading = false;
      $scope.csvUrl = graphCfg.api_url.replace(/\/jsv\??/, "/csv?additional_fields=1&");
      $scope.sqlUrl = graphCfg.api_url.replace(/\/jsv\??/, "/sql?additional_fields=1&");
      dataCountChart = dc.dataCount('.null');
      dataCountChart._doRender = function() {
        return $timeout(function() {
          $scope.total_count = dataCountChart.dimension().size();
          return $scope.filter_count = dataCountChart.group().value();
        });
      };
      usableData = [];
      $scope.uiParams = {
        builders: [],
        projects: [],
        branches: [],
        domains: [],
        platforms: [],
        components: [],
        types: [],
        priorities: [],
        initial_data: {}
      };
      $scope.attribute_links = {
        builders: {},
        projects: {},
        branches: {},
        domains: {},
        platforms: {},
        components: {},
        types: {},
        priorities: {}
      };
      $scope.dropDownsSelectionChange = {
        builders: false,
        projects: false,
        branches: false,
        domains: false,
        platforms: false,
        components: false,
        types: false,
        priorities: false
      };
      $scope.dependences = {
        builders: [],
        projects: ['builders'],
        branches: ['builders', 'projects'],
        domains: ['builders', 'projects', 'branches'],
        platforms: ['builders', 'projects', 'branches', 'domains'],
        components: ['builders', 'projects', 'branches', 'domains', 'platforms'],
        types: ['builders', 'projects', 'branches', 'domains', 'platforms', 'components'],
        priorities: ['builders', 'projects', 'branches', 'domains', 'platforms', 'components', 'types']
      };
      data.forEach(function(d, i) {
        var att, dataValue, dependences, dependentValue, err, getDataFieldValueByParam, j, k, len, ref, sD, u, v;
        if ((d.MergeDate != null) && d.MergeDate !== "None") {
          try {
            u = {};
            u.date = metricsService.parseCsvDate(d.MergeDate);
            u.BeforeReviewTime = +d.BeforeReviewTime;
            u.ReviewTime = +d.ReviewTime;
            u.MaintainerTime = +d.MaintainerTime;
            u.SubmitToMergeTime = +d.SubmitToMergeTime;
            u.MergeTime = +d.MergeTime;
            u.Branch = d.Branch;
            u.ComponentName = d.ComponentName;
            u.Id = d.Id;
            u.Builder = d.Builder;
            u.BugType = d.BugType;
            u.BugPriority = d.BugPriority;
            u.BugPlatform = d.BugPlatform;
            u.GitProject = d.GitProject;
            u.Domain = d.Domain;
            u.week = metricsService.getIntelWW(u.date);
          } catch (_error) {
            err = _error;
            u.week = "0000 00";
          }
          if (u.week === "0000 00" || u.IsMerged === 0 || isNaN(u.BeforeReviewTime) || isNaN(u.ReviewTime) || isNaN(u.MaintainerTime) || isNaN(u.SubmitToMergeTime) || isNaN(u.MergeTime) || u.BeforeReviewTime < 0 || u.ReviewTime < 0 || u.MaintainerTime < 0 || u.SubmitToMergeTime < 0 || u.MergeTime < 0) {
            return;
          }
          sD = metricsService.setDefault;
          getDataFieldValueByParam = function(param) {
            var value;
            value = "";
            switch (param) {
              case "builders":
                value = d.Builder;
                break;
              case "projects":
                value = d.GitProject;
                break;
              case "branches":
                value = d.Branch;
                break;
              case "platforms":
                value = d.BugPlatform;
                break;
              case "components":
                value = d.ComponentName;
                break;
              case "types":
                value = d.BugType;
                break;
              case "priorities":
                value = d.BugPriority;
                break;
              case "domains":
                value = d.Domain;
            }
            return value;
          };
          ref = $scope.dependences;
          for (k in ref) {
            v = ref[k];
            for (j = 0, len = v.length; j < len; j++) {
              att = v[j];
              dataValue = getDataFieldValueByParam(att);
              dependentValue = getDataFieldValueByParam(k);
              dependences = sD($scope.attribute_links[att], dataValue, {});
              sD(dependences, k, new Set()).add(dependentValue);
            }
          }
          usableData.push(u);
        }
      });
      $scope.ndx = ndx = crossfilter(usableData);
      $scope.all = all = ndx.groupAll();
      $scope.resetAll = function() {
        var k, new_value, ref, v;
        ref = $scope.uiParams.initial_data;
        for (k in ref) {
          v = ref[k];
          new_value = v.slice();
          $scope.uiParams[k] = new_value;
        }
        metricsService.resetFilter($scope.uiParams.git_projects, $scope.gitProjectDimensionList);
        metricsService.resetFilter($scope.uiParams.branches, $scope.branchDimensionList);
        metricsService.resetFilter($scope.uiParams.builders, $scope.builderDimensionList);
        metricsService.resetFilter($scope.uiParams.types, $scope.bugTypeDimensionList);
        metricsService.resetFilter($scope.uiParams.priorities, $scope.bugPriorityDimensionList);
        metricsService.resetFilter($scope.uiParams.platforms, $scope.bugPlatformDimensionList);
        metricsService.resetFilter($scope.uiParams.domains, $scope.domainDimensionList);
        $scope.init_component_drop_down_list();
        dc.filterAll();
        return dc.redrawAll();
      };
      implement_link = function(link_description) {
        var add_to_set, all_impacted, attribute, i_elts, impacted, impacted_in_selected, intersect, j, l, len, len1, len2, m, modified, modified_selected, ref, ref1, sets_sizes, smallest_set, smallest_set_index, ui_p, ui_selected, union_of_sets, union_set, v, x;
        modified = link_description.modified;
        impacted = link_description.impacted;
        ui_p = $scope.uiParams;
        if (ui_p.initial_data[impacted.attribute] == null) {
          i_elts = ui_p[impacted.attribute].slice();
          ui_p.initial_data[impacted.attribute] = i_elts;
        }
        all_impacted = ui_p.initial_data[impacted.attribute].slice();
        ui_selected = ui_p[modified.attribute];
        modified_selected = (function() {
          var j, len, results;
          results = [];
          for (j = 0, len = ui_selected.length; j < len; j++) {
            x = ui_selected[j];
            if (x.ticked) {
              results.push(x.name);
            }
          }
          return results;
        })();
        impacted_in_selected = new Set();
        union_of_sets = [];
        sets_sizes = [];
        union_set = new Set();
        add_to_set = function(value) {
          return union_set.add(value);
        };
        for (j = 0, len = modified_selected.length; j < len; j++) {
          v = modified_selected[j];
          $scope.attribute_links[modified.attribute][v][impacted.attribute].forEach(add_to_set);
        }
        union_of_sets.push(union_set);
        sets_sizes.push(union_set.size);
        ref = $scope.dependences[modified.attribute];
        for (l = 0, len1 = ref.length; l < len1; l++) {
          attribute = ref[l];
          union_set = new Set();
          ref1 = ui_p[attribute];
          for (m = 0, len2 = ref1.length; m < len2; m++) {
            x = ref1[m];
            if (x.ticked) {
              $scope.attribute_links[attribute][x.name][impacted.attribute].forEach(add_to_set);
            }
          }
          union_of_sets.push(union_set);
          sets_sizes.push(union_set.size);
        }
        smallest_set_index = sets_sizes.indexOf(Math.min.apply(null, sets_sizes));
        smallest_set = union_of_sets[smallest_set_index];
        impacted_in_selected = new Set();
        intersect = function(value) {
          var add_value, ind, set;
          add_value = true;
          for (ind in union_of_sets) {
            set = union_of_sets[ind];
            if (ind === smallest_set_index) {
              continue;
            }
            if (!set.has(value)) {
              add_value = false;
              break;
            }
          }
          if (add_value) {
            return impacted_in_selected.add(value);
          }
        };
        smallest_set.forEach(intersect);
        ui_p[impacted.attribute] = (function() {
          var len3, n, results;
          results = [];
          for (n = 0, len3 = all_impacted.length; n < len3; n++) {
            x = all_impacted[n];
            if (impacted_in_selected.has(x.name)) {
              results.push(x);
            }
          }
          return results;
        })();
        metricsService.filter($scope.uiParams[modified.attribute], $scope[modified.dimension]);
        return metricsService.filter($scope.uiParams[impacted.attribute], $scope[impacted.dimension]);
      };
      $scope.filter = function($scope, dimension) {
        metricsService.filter($scope, dimension);
        return dc.redrawAll();
      };
      $scope.all_records = data.length;
      $scope.all_filtered_records = data.length - usableData.length;
      data = {};
      dataCountChart.dimension(ndx);
      dataCountChart.group(all);
      $scope.weeklyDimension = ndx.dimension(function(d) {
        return d.week;
      });
      $scope.gitProjectDimensionList = ndx.dimension(function(d) {
        return d.GitProject;
      });
      $scope.gitProjectDimension = ndx.dimension(function(d) {
        return d.GitProject;
      });
      $scope.dropDownGitProject = metricsService.formatDropdownData($scope.uiParams.projects, $scope.gitProjectDimension);
      $scope.branchDimensionList = ndx.dimension(function(d) {
        return d.Branch;
      });
      $scope.branchDimension = ndx.dimension(function(d) {
        return d.Branch;
      });
      $scope.dropDownBranch = metricsService.formatDropdownData($scope.uiParams.branches, $scope.branchDimension);
      $scope.componentDimensionList = ndx.dimension(function(d) {
        return d.ComponentName;
      });
      $scope.componentDimension = ndx.dimension(function(d) {
        return d.ComponentName;
      });
      $scope.componentCountDimension = ndx.dimension(function(d) {
        return d.ComponentName;
      });
      $scope.dropDownComponent = metricsService.formatDropdownData($scope.uiParams.components, $scope.componentDimension);
      $scope.builderDimensionList = ndx.dimension(function(d) {
        return d.Builder;
      });
      $scope.builderDimension = ndx.dimension(function(d) {
        return d.Builder;
      });
      $scope.dropDownBuilder = metricsService.formatDropdownData($scope.uiParams.builders, $scope.builderDimension);
      $scope.bugTypeDimensionList = ndx.dimension(function(d) {
        return d.BugType;
      });
      $scope.bugTypeDimension = ndx.dimension(function(d) {
        return d.BugType;
      });
      $scope.dropDownBugType = metricsService.formatDropdownData($scope.uiParams.types, $scope.bugTypeDimension);
      $scope.bugPriorityDimensionList = ndx.dimension(function(d) {
        return d.BugPriority;
      });
      $scope.bugPriorityDimension = ndx.dimension(function(d) {
        return d.BugPriority;
      });
      $scope.dropDownBugPriority = metricsService.formatDropdownData($scope.uiParams.priorities, $scope.bugPriorityDimension);
      $scope.bugPlatformDimensionList = ndx.dimension(function(d) {
        return d.BugPlatform;
      });
      $scope.bugPlatformDimension = ndx.dimension(function(d) {
        return d.BugPlatform;
      });
      $scope.dropDownBugPlatforms = metricsService.formatDropdownData($scope.uiParams.platforms, $scope.bugPlatformDimension);
      $scope.domainDimensionList = ndx.dimension(function(d) {
        return d.Domain;
      });
      $scope.domainDimension = ndx.dimension(function(d) {
        return d.Domain;
      });
      $scope.dropDownDomain = metricsService.formatDropdownData($scope.uiParams.domains, $scope.domainDimension);
      $scope.cycleDimension = ndx.dimension(function(d) {
        return d.week;
      });
      $scope.componentCountDimensionGroup = $scope.componentCountDimension.group().reduceCount();
      $scope.componentCountDimensionGroup = function() {
        var count_group;
        count_group = $scope.componentCountDimension.group().reduceCount();
        return {
          all: function() {
            return count_group.all().filter(function(d) {
              return d.value >= 50;
            });
          }
        };
      };
      $scope.component_to_select_by_default = (function() {
        var j, len, ref, results;
        ref = $scope.componentCountDimensionGroup().all();
        results = [];
        for (j = 0, len = ref.length; j < len; j++) {
          x = ref[j];
          results.push(x.key);
        }
        return results;
      })();
      $scope.dropDownItemClick = function(data, field) {
        return $scope.dropDownsSelectionChange[field] = true;
      };
      create_attr_dimension = function(attr_name, dimension_name) {
        var res;
        res = {
          attribute: attr_name,
          dimension: dimension_name
        };
        return res;
      };
      $scope.filter_change = function(modified, modified_dim, impacted, impacted_dim, primary) {
        var link_description;
        if (primary) {
          if (!$scope.dropDownsSelectionChange[modified]) {
            return;
          }
          $scope.dropDownsSelectionChange[modified] = false;
        }
        link_description = {
          modified: create_attr_dimension(modified, modified_dim),
          impacted: create_attr_dimension(impacted, impacted_dim)
        };
        return implement_link(link_description);
      };
      $scope.set_cactusbranch = function(primary) {
        $scope.filter_change('builders', 'builderDimensionList', 'projects', 'gitProjectDimensionList', primary);
        $scope.set_gitproject(false);
        if (primary) {
          return dc.redrawAll();
        }
      };
      $scope.set_gitproject = function(primary) {
        $scope.filter_change('projects', 'gitProjectDimensionList', 'branches', 'branchDimensionList', primary);
        $scope.set_gitbranch(false);
        if (primary) {
          return dc.redrawAll();
        }
      };
      $scope.set_gitbranch = function(primary) {
        $scope.filter_change('branches', 'branchDimensionList', 'domains', 'domainDimensionList', primary);
        $scope.set_domain(false);
        if (primary) {
          return dc.redrawAll();
        }
      };
      $scope.set_domain = function(primary) {
        $scope.filter_change('domains', 'domainDimensionList', 'platforms', 'bugPlatformDimensionList', primary);
        $scope.set_bugplatform(primary);
        if (primary) {
          return dc.redrawAll();
        }
      };
      $scope.set_bugplatform = function(primary) {
        $scope.filter_change('platforms', 'bugPlatformDimensionList', 'components', 'componentDimensionList', primary);
        $scope.set_bugcomponent(false);
        if (primary) {
          return dc.redrawAll();
        }
      };
      $scope.set_bugcomponent = function(primary) {
        $scope.filter_change('components', 'componentDimensionList', 'types', 'bugTypeDimensionList', primary);
        $scope.set_bugtype(false);
        if (primary) {
          return dc.redrawAll();
        }
      };
      $scope.set_bugtype = function(primary) {
        $scope.filter_change('types', 'bugTypeDimensionList', 'priorities', 'bugPriorityDimensionList', primary);
        if (primary) {
          return dc.redrawAll();
        }
      };
      $scope.init_component_drop_down_list = function() {
        var j, len, ref, ref1;
        ref = $scope.uiParams.components;
        for (j = 0, len = ref.length; j < len; j++) {
          x = ref[j];
          x.ticked = (ref1 = x.name, indexOf.call($scope.component_to_select_by_default, ref1) >= 0) ? true : false;
        }
        return $scope.set_bugcomponent();
      };
      reduce_add = function(p, v) {
        ++p.count;
        p.sumBeforeReviewTime += +v.BeforeReviewTime;
        p.sumReviewTime += +v.ReviewTime;
        p.sumMaintainerTime += +v.MaintainerTime;
        p.sumSubmitToMergeTime += +v.SubmitToMergeTime;
        p.sumMergeTime += +v.MergeTime;
        return p;
      };
      reduce_del = function(p, v) {
        --p.count;
        p.sumBeforeReviewTime -= +v.BeforeReviewTime;
        p.sumReviewTime -= +v.ReviewTime;
        p.sumMaintainerTime -= +v.MaintainerTime;
        p.sumSubmitToMergeTime -= +v.SubmitToMergeTime;
        p.sumMergeTime -= +v.MergeTime;
        return p;
      };
      reduce_init = function() {
        return {
          count: 0,
          sumBeforeReviewTime: 0,
          sumReviewTime: 0,
          sumMaintainerTime: 0,
          sumSubmitToMergeTime: 0,
          sumMergeTime: 0
        };
      };
      remove_empty_bins = function(source_group) {
        return {
          all: function() {
            return source_group.all().filter(function(d) {
              return d.value.count > 0;
            });
          }
        };
      };
      $scope.builderDimensionGroup = $scope.builderDimension.group().reduce(reduce_add, reduce_del, reduce_init);
      $scope.builderChartFilteredDimensionGroup = remove_empty_bins($scope.builderDimensionGroup);
      $scope.gitBranchDimensionGroup = $scope.branchDimension.group().reduce(reduce_add, reduce_del, reduce_init);
      $scope.gitBranchChartFilteredDimensionGroup = remove_empty_bins($scope.gitBranchDimensionGroup);
      $scope.domainDimensionGroup = $scope.domainDimension.group().reduce(reduce_add, reduce_del, reduce_init);
      $scope.domainChartFilteredDimensionGroup = remove_empty_bins($scope.domainDimensionGroup);
      $scope.bugPlatformDimensionGroup = $scope.bugPlatformDimension.group().reduce(reduce_add, reduce_del, reduce_init);
      $scope.bugPlatformChartFilteredDimensionGroup = remove_empty_bins($scope.bugPlatformDimensionGroup);
      $scope.cycleDimensionGroup = $scope.cycleDimension.group().reduce(reduce_add, reduce_del, reduce_init);
      $scope.bugTypeDimensionGroup = $scope.bugTypeDimension.group().reduce(reduce_add, reduce_del, reduce_init);
      $scope.bugTypeChartFilteredDimensionGroup = remove_empty_bins($scope.bugTypeDimensionGroup);
      $scope.bugPriorityDimensionGroup = $scope.bugPriorityDimension.group().reduce(reduce_add, reduce_del, reduce_init);
      $scope.bugPriorityChartFilteredDimensionGroup = remove_empty_bins($scope.bugPriorityDimensionGroup);
      $scope.componentDimensionGroup = $scope.componentDimension.group().reduce(reduce_add, reduce_del, reduce_init);
      $scope.componentChartFilteredDimensionGroup = remove_empty_bins($scope.componentDimensionGroup);
      $scope.stackedBarChartConfigure = function(chart, group, dimension_title) {
        chart.group(group, 'avgBeforeReviewTime').valueAccessor(function(d) {
          return metricsService.intDisplayFormat(d.value.sumBeforeReviewTime / d.value.count);
        }).stack(group, "avgReviewTime", function(d) {
          return metricsService.intDisplayFormat(d.value.sumReviewTime / d.value.count);
        }).stack(group, "avgMaintainerTime", function(d) {
          return metricsService.intDisplayFormat(d.value.sumMaintainerTime / d.value.count);
        }).stack(group, "avgSubmitToMergeTime", function(d) {
          return metricsService.intDisplayFormat(d.value.sumSubmitToMergeTime / d.value.count);
        }).stack(group, "avgMergeTime", function(d) {
          return metricsService.intDisplayFormat(d.value.sumMergeTime / d.value.count);
        }).on('renderlet', function(c) {
          return metricsService.setOrdonalAxis(c);
        }).title(function(d) {
          var sumTotal, title;
          sumTotal = 0;
          chart.stack().forEach(function(k, i) {
            if (!k.hidden) {
              return sumTotal += d.value[k.name.replace('avg', 'sum')];
            }
          });
          title = metricsService.padding_right(dimension_title + ':', 32) + d.key + "\n" + metricsService.padding_right('Nbr:', 32) + d.value.count + "\n\n";
          chart.stack().forEach(function(k, i) {
            var key;
            if (!k.hidden) {
              key = k.name.replace('avg', '');
              return title += metricsService.displayKeyTimePercent(key.replace('Time', '') + ":", d.value['sum' + key] / d.value.count, d.value['sum' + key] / sumTotal * 100);
            }
          });
          return title;
        });
        return chart.yAxis().tickFormat(d3.format(",d"));
      };
      $scope.domainChartConfigure = function(c) {
        return $scope.stackedBarChartConfigure(c, $scope.domainChartFilteredDimensionGroup, "Patch Domain");
      };
      $scope.cycleChartConfigure = function(c) {
        $scope.stackedBarChartConfigure(c, $scope.cycleDimensionGroup, "Work Week");
        return c.on('renderlet', function(c) {
          return metricsService.setWWAxis(c);
        });
      };
      $scope.builderChartConfigure = function(c) {
        return $scope.stackedBarChartConfigure(c, $scope.builderChartFilteredDimensionGroup, "Cactus Branch");
      };
      $scope.gitBranchChartConfigure = function(c) {
        return $scope.stackedBarChartConfigure(c, $scope.gitBranchChartFilteredDimensionGroup, "Git Branch");
      };
      $scope.bugPlatformChartConfigure = function(c) {
        return $scope.stackedBarChartConfigure(c, $scope.bugPlatformChartFilteredDimensionGroup, "Bug Platform/Program");
      };
      $scope.bugTypeChartConfigure = function(c) {
        return $scope.stackedBarChartConfigure(c, $scope.bugTypeChartFilteredDimensionGroup, "Bug Type");
      };
      $scope.bugPriorityChartConfigure = function(c) {
        return $scope.stackedBarChartConfigure(c, $scope.bugPriorityChartFilteredDimensionGroup, "Bug Priority");
      };
      $scope.componentChartConfigure = function(c) {
        return $scope.stackedBarChartConfigure(c, $scope.componentChartFilteredDimensionGroup, "Bug Component");
      };
      $scope.NbPatchBarChartConfigure = function(chart, dimension_title) {
        return chart.valueAccessor(function(d) {
          return d.value.count;
        }).title(function(d) {
          return dimension_title + ": " + d.key + "\n" + "\nNbr: " + d.value.count;
        }).on('renderlet', function(chart) {
          return metricsService.setOrdonalAxis(chart);
        });
      };
      $scope.wwNbPatchBarChartSetup = function(c) {
        $scope.NbPatchBarChartConfigure(c, 'Work Week');
        return c.on('renderlet', function(c) {
          return metricsService.setWWAxis(c);
        });
      };
      $scope.builderNbPatchBarChartSetup = function(c) {
        return $scope.NbPatchBarChartConfigure(c, 'Cactus Branch');
      };
      $scope.bugPlatformNbPatchBarChartSetup = function(c) {
        return $scope.NbPatchBarChartConfigure(c, 'Bug Platform/Program');
      };
      $scope.domainNbPatchBarChartSetup = function(c) {
        return $scope.NbPatchBarChartConfigure(c, 'Patch Domain');
      };
      $scope.gitBranchNbPatchBarChartSetup = function(c) {
        return $scope.NbPatchBarChartConfigure(c, 'Git Branch');
      };
      $scope.bugTypeNbBarChartSetup = function(c) {
        return $scope.NbPatchBarChartConfigure(c, 'Bug Type');
      };
      $scope.bugPriorityNbPatchBarChartSetup = function(c) {
        return $scope.NbPatchBarChartConfigure(c, 'Bug Priority');
      };
      $scope.componentNbPatchBarChartSetup = function(c) {
        return $scope.NbPatchBarChartConfigure(c, 'Bug Component');
      };
      $scope.tableGroup = function(d) {
        return "WW" + d.week;
      };
      $scope.tablePostFormat = function(c) {
        c.columns([
          {
            label: "Patch Id",
            format: function(d) {
              return "<a href=\"" + config.urls.gerrit_url + d.Id + "\" target=_blank>" + d.Id + "</a>";
            }
          }, {
            label: "Date",
            format: function(d) {
              return d3.time.format("%d/%m/%y")(d.date);
            }
          }, {
            label: "Before Review Time",
            format: function(d) {
              return d.BeforeReviewTime;
            }
          }, {
            label: "Review Time",
            format: function(d) {
              return d.ReviewTime;
            }
          }, {
            label: "Maintainer Time",
            format: function(d) {
              return d.MaintainerTime;
            }
          }, {
            label: "Submit To Merge Time",
            format: function(d) {
              return d.SubmitToMergeTime;
            }
          }, {
            label: "Merge Time",
            format: function(d) {
              return d.MergeTime;
            }
          }
        ]).sortBy(function(d) {
          var res;
          res = d3.time.format("%d/%m/%y")(d.date) + d.Id;
          return res;
        }).order(d3.descending);
        $scope.db = c;
        return $scope.nb_columns_original = c.columns().length;
      };
      $scope.init_component_drop_down_list();
    });
  });

}).call(this);
import itertools
import random
import time
from datetime import datetime

from .models.enums import *
from .models.randomizer_data import RandomizerData

from .data.area_short_name import get_area_short_name
from .data.default_enemies import DEFAULT_ENEMIES
from .data.enemies import ENEMIES
from .data.enemizer_restricted_enemies import ENEMIZER_RESTRICTED_ENEMIES
from .data.enemy_sets import ENEMY_SETS
from .data.exit_logic import get_exit_logic
from .data.exits import get_exits
from .data.form_items import FORM_ITEMS
from .data.graph import get_graph
from .data.item_locations import get_item_locations
from .data.item_pool import get_item_pool
from .data.logic import get_logic
from .data.maps import get_maps
from .data.overworld_menus import OVERWORLD_MENUS
from .data.spawn_locations import get_spawn_locations
from .data.spoiler_labels import SPOILER_LABELS

MAX_INVENTORY = 15
PROGRESS_ADJ = [1.5, 1.25, 1.0, 0.75]  # Required items are more likely to be placed in easier modes
MAX_CYCLES = 200


class World:
    # Severity: 0 = error/breakpoint, 1 = warning, 2 = info, 3 = verbose.
    def log(self, message, severity=0):
        prefixes = ["Error: ", "Warning: ", "", ""]
        prefix = prefixes[severity]
        if severity <= 1:
            self.errorlog.append(prefix + message)
        if severity <= self.printlevel:
            print(prefix + message)
        return

    # Aliases, if using them is clearer to you
    def verbose(self, message):
        return self.log(message, 3)

    def info(self, message):
        return self.log(message, 2)

    def warn(self, message):
        return self.log(message, 1)

    def error(self, message):
        self.log(message, 0)
        if self.break_on_error:
            breakpoint()
        return

    # Some basic validations for profiling
    def validate(self):
        val_messages = []
        val_success = True
        placed_item_counts = {}
        for loc in self.item_locations:
            if self.item_locations[loc][1] not in [1,2,3,5]:
                continue
            item = self.item_locations[loc][3]
            loc_pool = self.item_locations[loc][7]
            if item == 0 and self.item_locations[loc][1] == 2:
                continue
            if self.item_pool[item][6] == 0 and loc_pool == 0:
                continue
            if item not in placed_item_counts:
                placed_item_counts[item] = 0
            placed_item_counts[item] += 1
            if item not in self.item_pool:
                val_success = False
                val_messages.append("Item val error: Loc " + str(loc) + " contains deleted item " + str(item))
            elif self.item_pool[item][6] != loc_pool:
                val_success = False
                val_messages.append(
                    "Item val error: Pool of loc " + str(loc) + " doesn't match pool of item " + str(item))
        for item in placed_item_counts:
            if placed_item_counts[item] != self.base_item_counts[item]:
                val_success = False
                val_messages.append("Item val error: Item " + str(item) + " placed " + str(
                    placed_item_counts[item]) + " times but expected " + str(self.base_item_counts[item]))
        if val_success:
            val_messages.append("Item val passed")
        val_success = True
        if self.orb_rando != "None" and not self.dungeon_shuffle:
            # Check whether certain problem orbs are locked behind themselves
            for eddg_end_loc in [17, 18, 19, 705, 706]:
                if eddg_end_loc in self.item_locations and self.item_locations[eddg_end_loc][3] == 704:
                    val_success = False
                    val_messages.append("Orb val error: EdDg DS orb is inaccessible")
                    break
        if val_success:
            val_messages.append("Orb val passed")
        return val_messages

    # Assigns item to location
    def fill_item(self, item, location=-1, test=False, override_restrictions=False):
        if location == -1:
            return False
        elif not test and self.item_locations[location][2]:
            self.verbose("Tried to place an item in a full location: " + str(self.item_pool[item][3]) + " " + str(
                self.item_locations[location][6]))
            return False
        elif not test and item in self.item_locations[location][4] and not override_restrictions:
            self.verbose("Tried to place item in a restricted location: " + str(self.item_pool[item][3]) + " " + str(
                self.item_locations[location][6]))
            return False
        elif test:
            return True

        self.item_pool[item][0] -= 1
        self.item_locations[location][2] = True
        self.item_locations[location][3] = item

        self.verbose("  " + str(self.item_pool[item][3]) + " -> " + str(self.item_locations[location][6]))

        if self.is_accessible(self.item_locations[location][0]):
            self.items_collected.append(item)
            self.open_locations[self.item_locations[location][7]].remove(location)

        self.placement_log.append([item, location])
        return True

    # Removes an assigned item and returns it to item pool
    def unfill_item(self, location=-1):
        if location not in self.item_locations or not self.item_locations[location][2]:
            return -1

        item = self.item_locations[location][3]
        self.item_locations[location][2] = False
        self.item_locations[location][3] = 0
        self.item_pool[item][0] += 1

        self.verbose("  " + str(self.item_pool[item][3]) + "<-" + str(self.item_locations[location][6]) + " removed")

        if self.is_accessible(self.item_locations[location][0]):
            if item in self.items_collected:
                self.items_collected.remove(item)
            pool = self.get_pool_id(item=item)
            if location not in self.open_locations[pool]:
                self.open_locations[pool].append(location)

        for x in self.placement_log:
            if x[1] == location:
                self.placement_log.remove(x)

        return item

    # Map a type/item/location to a shuffle pool ID.
    # Returns pool 0 if a type/item/location isn't shuffled.
    def get_pool_id(self, type=-1, item=-1, loc=-1):
        if type < 0:
            if item in self.item_pool:
                type = self.item_pool[item][1]
            elif loc in self.item_locations:
                type = self.item_locations[loc][1]
            else:
                return 0
        if type == 1:
            return 1
        elif type == 2:
            return 2
        # elif type == 3:
        #    pass   # Statues aren't shuffled
        # elif type == 4:
        #    pass   # Artificial event flags aren't shuffled
        elif type == 5:
            if self.orb_rando == "Basic":
                return 5
            elif self.orb_rando == "Orbsanity":
                return 1
        elif type > self.get_max_pool_id():
            self.error("Type " + str(type) + " exceeds max pool ID")
            return 0
        return 0

    # Many lists are instantiated with one element per pool, so we need to know how
    # large to make those lists. This constant is validated via get_pool_id.
    def get_max_pool_id(self):
        return 6

    # Returns whether the item and location are in the same shuffle pool
    def are_item_loc_pooled(self, item, loc):
        return (self.get_pool_id(item=item) == self.get_pool_id(loc=loc))

    # Get list of items of given or all types, of any or all progression types.
    def list_typed_items(self, types, progress_type=0, shuffled_only=False, incl_placed=False):
        item_list = []
        for x in self.item_pool:
            if not types or self.item_pool[x][1] in types:
                if not progress_type or progress_type == self.item_pool[x][5]:
                    if not shuffled_only or self.item_pool[x][6] > 0:
                        for _ in range(self.item_pool[x][0]):
                            item_list.append(x)
                        if incl_placed:
                            for _ in [loc for loc in self.item_locations if self.item_locations[loc][3] == x]:
                                item_list.append(x)
        return item_list

    # Get list of items shuffled with given or all types, of any or all progression types.
    # If shuffled_only, items that aren't randomized (based on seed settings) are omitted.
    def list_pooled_items(self, types, progress_type=0, shuffled_only=False, incl_placed=False):
        if not types:
            return self.list_typed_items([], progress_type, shuffled_only, incl_placed)
        pools = set(self.get_pool_id(type=x) for x in types)
        item_list = []
        for x in self.item_pool:
            if self.item_pool[x][6] in pools:
                if not progress_type or progress_type == self.item_pool[x][5]:
                    if not shuffled_only or self.item_pool[x][6] > 0:
                        for _ in range(self.item_pool[x][0]):
                            item_list.append(x)
                        if incl_placed:
                            for _ in [loc for loc in self.item_locations if self.item_locations[loc][3] == x]:
                                item_list.append(x)
        return item_list

    # Returns all item locations
    def list_item_locations(self, shuffled_only=True):
        locations = []
        for x in self.item_locations:
            if self.item_locations[x][7] or not shuffled_only:
                locations.append(x)
        return locations

    # Returns list of graph edges
    def list_logic(self):
        edges = []
        for x in self.logic:
            edges.append(x)
        return edges

    # Checks if one list is contained inside another list
    def is_sublist(self, list, sublist):
        if sublist == []:
            return True
        elif len(sublist) > len(list):
            return False
        l = list[:]
        for x in sublist:
            if x in l:
                l.remove(x)
            else:
                return False
        return True

    # Returns graph node of an item location
    def location_node(self, location_id=-1):
        if location_id not in self.item_locations:
            self.error("Invalid item location " + str(location_id))
            return False
        else:
            return self.item_locations[location_id][0]

    # Returns whether an item location is already filled with an item
    def is_filled(self, location_id=-1):
        if location_id not in self.item_locations:
            self.error("Invalid item location " + str(location_id))
            return False
        else:
            return self.item_locations[location_id][2]

    # Returns whether the node is within the currently-accessible subgraph
    def is_accessible(self, node_id=-1):
        if node_id not in self.graph:
            return False
        elif self.graph[node_id][0]:
            return True
        else:
            return False

    # Zeroes out accessible flags for all world regions
    def unsolve(self, reset_graph=False):
        for x in self.graph:
            self.graph[x][0] = False
            if reset_graph:
                self.graph[x][4] = 0
                self.graph[x][8].clear()
                self.graph[x][9].clear()
                self.graph[x][10] = self.graph[x][1][:]
        for x in self.logic:
                self.logic[x][0] = 0
        return True

    # Resets collected items and other traversal data
    def reset_progress(self, reset_graph=False):
        self.visited.clear()
        self.items_collected.clear()
        self.item_destinations.clear()
        self.open_locations = [[] for _ in range(self.item_pool_count)]
        self.open_edges = []
        self.unsolve(reset_graph)
        return True

    # Returns every accessible node from to_visit. Marks edges as traversed. 
    # If not test: marks nodes as traversed, collects self.items_collected/self.open_edges,
    # adds graph connections, and updates DS access.
    # Bug: if W can't reach a ForceWillForm node but F/S can, this traverses the node without propagating any
    # form access. I think currently this just causes a small number of boss shuffle + ER seeds to be
    # incorrectly rejected as unwinnable.
    def traverse(self, to_visit=[], test=False):
        self.verbose(" Beginning traversal...")
        visited = []
        new_items = []
        if not to_visit:
            to_visit.append(0)
        while to_visit:
            node = to_visit.pop(0)
            visited.append(node)
            self.verbose("  Visiting node " + str(node) + " " + str(self.graph[node][5]))
            # If we haven't been here yet...
            if not self.graph[node][0]:
                # Get the newly-accessible items and record open item/ability locations
                new_items += self.visit_node(node, test)
                # Queue up newly-accessible nodes to visit
                for x in self.graph[node][1]:
                    if x != node and x not in to_visit + visited:
                        to_visit.insert(0, x)
                        self.verbose("  -Found node " + str(x) + " " + str(self.graph[x][5]))
            # Propagate form access
            if not test:
                access_mode = self.graph[node][4]
                if node in self.txform_nodes:
                    access_mode |= (0x01|0x02|0x04)
                self.update_ds_access([node], access_mode, self.graph[node][9])
            # If we've run out of nodes to visit, check if logic has opened up any new nodes
            if not to_visit:
                open_edges = self.get_open_edges(visited, True)
                bad_edges = []
                # self.verbose(" All known nodes checked. Traversing edges...")
                for edge in open_edges:
                    origin = self.logic[edge][1]
                    dest = self.logic[edge][2]
                    if self.check_edge(edge, [], not test, self.graph[origin][4]):
                        self.logic[edge][0] = 1
                        if dest not in to_visit:
                            to_visit.append(dest)
                            self.verbose("  -Found node " + str(dest) + " " + str(self.graph[dest][5]))
                    else:
                        bad_edges.append(edge)
                if not test:
                    self.open_edges = bad_edges
        return [visited, new_items]

    # Return list of logic edges that originate in an accessible node in nodes, and
    # either are locked or terminate outside of nodes.
    # include_redundant to include edges whose destination is already traversed.
    def get_open_edges(self, nodes=[], include_redundant=False):
        test_edges = self.open_edges[:]
        open_edges = []
        for x in nodes:
            if not self.is_accessible(x):
                test_edges += self.graph[x][12]
        for edge in test_edges:
            origin = self.logic[edge][1]
            dest = self.logic[edge][2]
            if (self.logic[edge][0] >= 0) and (edge not in open_edges) and (not self.is_accessible(dest) or self.graph[origin][4] != self.graph[dest][4] or include_redundant) and (dest not in nodes or self.logic[edge][0] == 0):
                open_edges.append(edge)
        return open_edges

    # Visit a node, update graph info, return new items collected
    def visit_node(self, node, test=False):
        if not test and not self.graph[node][0]:
            self.graph[node][0] = True
            self.visited.append(node)
            self.item_destinations += self.graph[node][6]
            self.open_edges += self.graph[node][12]
        return self.collect_items(node, test)

    # Collect all items in given node
    def collect_items(self, node=-1, test=False):
        if node not in self.graph:
            return False
        items_found = []
        for location in self.graph[node][11]:
            if self.item_locations[location][2]:
                items_found.append(self.item_locations[location][3])
                if not test:
                    self.items_collected.append(self.item_locations[location][3])
                self.verbose("  -Got item " + str(self.item_locations[location][3]) + " " + str(
                    self.item_pool[self.item_locations[location][3]][3]) + " from loc " + str(location) + " " + str(
                    self.item_locations[location][6]).strip() + " in node " + str(node) + " " + str(
                    self.graph[node][5]).strip())
            elif not test:
                self.open_locations[self.item_locations[location][7]].append(location)
                # self.verbose("  -Found empty loc "+str(location)+" "+str(self.item_locations[location][6]))
        return items_found

    # Returns full list of accessible locations
    def accessible_locations(self, item_locations):
        accessible = []
        for x in item_locations:
            region = self.item_locations[x][0]
            if self.is_accessible(region):
                accessible.append(x)
        return accessible

    # Returns full list of inaccessible locations
    def inaccessible_locations(self, item_locations):
        inaccessible = []
        for x in item_locations:
            region = self.item_locations[x][0]
            if not self.is_accessible(region):
                inaccessible.append(x)
        return inaccessible

    # Fill a list of type-1 items randomly in a list of type-1 locations
    def random_fill(self, items=[], item_locations=[], accessible=True):
        if not items:
            return True
        elif not item_locations:
            return False

        to_place = items[:]
        to_fill = [loc for loc in item_locations[:] if not self.item_locations[loc][2]]

        while to_place:
            item = to_place.pop(0)
            for dest in to_fill:
                region = self.item_locations[dest][0]
                filled = self.item_locations[dest][2]
                restrictions = self.item_locations[dest][4]
                if not filled and self.are_item_loc_pooled(item, dest) and item not in restrictions:
                    if not accessible or region >= 0:
                        if self.fill_item(item, dest, False, False):
                            to_fill.remove(dest)
                            break

        return True

    # Place list of items into random accessible locations
    def forward_fill(self, items=[], item_locations=[], test=False, override_restrictions=False, impose_penalty=False):
        if not items:
            return True
        elif not item_locations:
            # self.verbose("forward_fill given items but no locations")
            return False

        to_place = items[:]
        if impose_penalty and not any(self.item_pool[item][7] > 0 for item in to_place):
            impose_penalty = False  # Don't go through penalty code if there are no penalized items
        if impose_penalty:  # More restrictive items are placed first
            to_place.sort(key=lambda item: -1 * self.item_pool[item][7])
        to_fill = [[] for _ in range(self.item_pool_count)]
        loc_quarantine = [[] for _ in range(self.item_pool_count)]
        for pool in range(self.item_pool_count):
            to_fill[pool] = [loc for loc in item_locations if self.item_locations[loc][7] == pool and not self.item_locations[loc][2] and self.is_accessible(self.item_locations[loc][0])]
            if impose_penalty:  # Later locations are preferred by more restrictive items
                to_fill[pool].sort(key=lambda loc: -1 * self.item_locations[loc][8])
            else:
                random.shuffle(to_fill[pool])
        filled_locations = []
        while to_place:
            item = to_place.pop(0)
            pool = self.item_pool[item][6]
            preferred_locs = []
            if impose_penalty and self.item_pool[item][7] > 0 and len(to_fill[pool]) > 3:
                # Item penalty N ignores the earliest N deciles, if there are enough locs to do so
                preferred_locs = [to_fill[pool][0]]
                priority_cutoff = len(to_fill[pool]) * (1.0 - (float(self.item_pool[item][7]) / 10.0))
                while len(preferred_locs) < priority_cutoff:
                    preferred_locs.append(to_fill[pool][len(preferred_locs)])
            filled = False
            while not filled and (preferred_locs or to_fill[pool]):
                if preferred_locs:
                    location = preferred_locs.pop()
                    to_fill[pool].remove(location)
                else:
                    location = to_fill[pool].pop(0)
                if self.fill_item(item, location, test, override_restrictions):
                    filled = True
                    filled_locations.append(location)
                    to_fill[pool] += loc_quarantine[pool]
                else:
                    loc_quarantine[pool].append(location)
            if not filled:
                self.verbose("Not enough room to place item " + str(item))
                if not test:
                    for loc in filled_locations:
                        self.unfill_item(loc)
                return False

        return True

    # Convert a prerequisite to a list of items needed to fulfill it
    def items_needed(self, edge=0):
        if not edge:
            return []

        prereq = []
        for req in self.logic[edge][4]:
            item = req[0]
            ct = req[1]
            i = 0
            while i < ct:
                prereq.append(item)
                i += 1

        if not self.items_collected:
            return prereq

        prereq_new = []
        items_new = self.items_collected[:]

        while prereq:
            x = prereq.pop(0)
            if x in items_new:
                items_new.remove(x)
            else:
                prereq_new.append(x)

        return prereq_new

    # Returns list of item combinations that grant progression
    # Returns progression list in the following categories: [[available],[not enough room],[too many inventory items]]
    def progression_list(self, open_edges=[], ignore_inv=False, penalty_threshold=MAX_CYCLES):
        if not open_edges:
            open_edges = self.get_open_edges()
        all_items = [item for item in self.list_pooled_items(types=[], shuffled_only=True) if self.item_pool[item][7] <= penalty_threshold]
        prereq_list = [[], [], []]  # [[available],[not enough room],[too many inventory items]]
        ds_list = []

        for edge in open_edges:
            prereq = self.items_needed(edge)
            if prereq and prereq not in prereq_list[0] and self.is_sublist(all_items, prereq):
                all_open_locs = []
                for locpool in self.open_locations:
                    all_open_locs.extend(locpool)
                if prereq not in prereq_list[1] and not self.forward_fill(prereq, all_open_locs, True,
                                                                          self.logic_mode == "Chaos"):
                    prereq_list[1].append(prereq)
                elif prereq not in prereq_list[2]:
                    dest = self.logic[edge][2]
                    traverse_result = self.traverse([dest], True)
                    new_nodes = traverse_result[0]
                    start_items_temp = self.items_collected[:] + prereq + traverse_result[1]
                    item_destinations_temp = self.item_destinations[:]
                    for x in new_nodes:
                        item_destinations_temp += self.graph[x][6]
                    inv_temp = self.get_inventory(start_items_temp, item_destinations_temp)
                    if ignore_inv or len(inv_temp) <= MAX_INVENTORY:
                        if True:  # not self.entrance_shuffle or self.check_ds_access(dest,0x10,True,[]):
                            prereq_list[0].append(prereq)
                        else:
                            ds_list.append(prereq)
                    else:
                        prereq_list[2].append(prereq)

        if prereq_list == [[], [], []]:
            prereq_list[0] += ds_list

        return prereq_list

    # Remove a non-progression item to make room for a progression item.
    # Only works on type-1 items and type-1 locations.
    def make_room(self, progression_result):
        # For inventory bottlenecks, remove one inventory item and try again
        if not progression_result[1] and progression_result[2]:
            return self.remove_nonprog(1, True)
        for node in self.visited:
            for x in self.graph[node][11]:
                if self.is_filled(x) and self.item_locations[x][7] == 1 and self.item_pool[self.item_locations[x][3]][
                    5] > 1 and self.item_pool[self.item_locations[x][3]][6] == 1:
                    if self.unfill_item(x):
                        return True
        return False

    # Remove accessible non-progression items to make room for a progression item.
    def remove_nonprog(self, item_ct=0, inv=False):
        junk_locations = []
        quest_locations = []

        for location in self.item_locations:
            if self.item_locations[location][2] and self.item_locations[location][7] == 1 and self.is_accessible(
                    self.item_locations[location][0]):
                item = self.item_locations[location][3]
                prog_type = self.item_pool[item][5]
                inv_type = self.item_pool[item][4]
                if prog_type == 2:
                    quest_locations.append(location)
                elif prog_type == 3:
                    if not inv or inv_type:
                        junk_locations.append(location)
        random.shuffle(junk_locations)
        random.shuffle(quest_locations)

        quest = False
        locations = junk_locations
        count = item_ct
        done = False
        items_removed = []
        while not done:
            if not count:
                done = True
            else:
                if not locations and not quest:
                    quest = True
                    locations = quest_locations
                if not locations:
                    self.error("No room for prog items and no nonprog items to remove")
                    return False
                location = locations.pop(0)
                items_removed.append(self.unfill_item(location))
                count -= 1
        self.verbose("   Removed nonprog items: " + str(items_removed))
        return items_removed

    # Converts a progression list into a normalized Monte Carlo distribution
    def monte_carlo(self, progression_ls=[], start_items=[]):
        if not progression_ls:
            return []

        progression = progression_ls[:]

        items = self.list_typed_items(types=[1], shuffled_only=True)
        abilities = self.list_typed_items(types=[2], shuffled_only=True)
        orbs = self.list_typed_items(types=[5], shuffled_only=True)
        all_items = items + abilities + orbs
        sum_items = len(items)
        sum_abilities = len(abilities)
        sum_orbs = len(orbs)

        probability = []

        monte_carlo = []
        sum_prob = 0
        sum_edges = 0

        probabilities = []
        idx = 0
        while progression:
            current_prereq = progression.pop(0)
            prereqs = current_prereq[:]
            probability = 1.0
            i = 0
            j = 0
            k = 0
            while prereqs:
                item = prereqs.pop(0)
                if item in all_items:
                    if self.item_pool[item][1] == 1:
                        probability *= float(self.item_pool[item][0]) / float((sum_items - i))
                        i += 1
                    elif self.item_pool[item][1] == 2:
                        probability *= float(self.item_pool[item][0]) / float((sum_abilities - j))
                        j += 1
                    elif self.item_pool[item][1] == 5:
                        probability *= float(self.item_pool[item][0]) / float((sum_orbs - k))
                        k += 1
                    probability *= (10.1 - float(self.item_pool[item][7])) / 10.0
                    if item in self.required_items:
                        probability *= PROGRESS_ADJ[self.difficulty]
            probabilities.append([probability, idx])
            sum_prob += probability
            sum_edges += 1
            idx += 1

        prob_adj = 100.0 / sum_prob
        rolling_sum = 0.0
        for x in probabilities:
            x[0] = x[0] * prob_adj + rolling_sum
            rolling_sum = x[0]

        # print probabilities
        return probabilities

    # Returns a list of map lists, by boss
    def get_maps(self):
        maps = [[], [], [], [], [], [], []]
        for map in self.maps:
            if self.maps[map][0] >= 0 and not (self.maps[map][8] and (self.dungeon_shuffle or self.difficulty == 0)):    # Jumbo maps don't get rewards in dungeon shuffles or on Easy
                boss = self.maps[map][1]
                maps[boss].append(map)
        maps.pop(0)  # Non-dungeon maps aren't included
        return maps

    # Randomize map-clearing rewards
    def map_rewards(self):
        maps = self.get_maps()
        for area in maps:
            random.shuffle(area)

        # Total rewards by type, by level (HP/STR/DEF)
        if "Z3 Mode" in self.variant:
            rewards_tier1 = [1] * 6  # Expert: 6 HP
            rewards_tier2 = [1] * 6  # Advanced: 12 HP
            rewards_tier3 = [1] * 6  # Intermediate: 18 HP
            rewards_tier4 = []  # Beginner: 18 HP
        else:  # Remove all HP upgrades
            rewards_tier1 = [1, 1, 1, 1, 1, 1]  # Expert: 6/0/0
            rewards_tier2 = [1, 1, 2, 2, 3, 3]  # Advanced: 8/2/2
            rewards_tier3 = [1, 1, 2, 2, 3, 3]  # Intermediate: 10/4/4
            rewards_tier4 = [2, 2, 2, 3, 3, 3]  # Beginner: 10/7/7

        # Remove HP upgrades in OHKO
        if "OHKO" in self.variant:
            for n, i in enumerate(rewards_tier1):
                if i == 1:
                    rewards_tier1[n] = 0
            for n, i in enumerate(rewards_tier2):
                if i == 1:
                    rewards_tier2[n] = 0
            for n, i in enumerate(rewards_tier3):
                if i == 1:
                    rewards_tier3[n] = 0
            for n, i in enumerate(rewards_tier4):
                if i == 1:
                    rewards_tier4[n] = 0

        random.shuffle(rewards_tier1)
        random.shuffle(rewards_tier2)
        random.shuffle(rewards_tier3)
        random.shuffle(rewards_tier4)

        # Allocate rewards to maps
        for area in maps:
            random.shuffle(area)
            self.maps[area[0]][2] = [rewards_tier1.pop(0), 1]
            self.maps[area[1]][2] = [rewards_tier2.pop(0), 2]
            self.maps[area[2]][2] = [rewards_tier3.pop(0), 3]
            if rewards_tier4:
                self.maps[area[3]][2] = [rewards_tier4.pop(0), 4]
            else:
                self.maps[area[3]][2] = [0, 4]

    # Place Mystic Statues in World
    def fill_statues(self, locations=[148, 149, 150, 151, 152, 153]):
        if self.statue_req == StatueReq.PLAYER_CHOICE.value:
            return self.random_fill([106] * 6, locations)
        return self.random_fill([100, 101, 102, 103, 104, 105], locations)

    # If the vanilla exit is two-way (i.e. has a paired exit), returns the paired exit.
    # Otherwise, returns 0 to indicate the exit is one-way or doesn't exist.
    def is_exit_coupled(self, exit):
        if exit not in self.exits:
            return 0
        if self.exits[exit][0]:
            sister_exit = self.exits[exit][0]
            if self.exits[sister_exit][0] == exit:
                return sister_exit
            else:
                self.warn("Exits linked incorrectly " + str(exit) + " " + str(sister_exit))
                return sister_exit
        return 0

    # Determine an exit's direction (e.g. outside to inside).
    # An exit from a "roof" (type-3 node) always counts as going outside,
    # to discourage attaching dead-end interior rooms to roof exits.
    def exit_direction(self, exit):
        if exit not in self.exits:
            return False
        origin = self.exits[exit][3]
        dest = self.exits[exit][4]
        if self.graph[origin][2] == 2:
            o_type = 2
        else:
            o_type = 1
        if self.graph[origin][3] == 3:
            d_type = 1
        else:
            if self.graph[dest][2] == 2:
                d_type = 2
            else:
                d_type = 1
        if o_type == 2 and d_type == 2:
            return (1, 1)
        else:
            return d_type

    # Link one exit to another, making origin_exit act like dest_exit; that is,
    # replace the transition data of origin_exit with the vanilla transition data of dest_exit.
    def link_exits(self, origin_exit, dest_exit, check_connections=True, update_graph=True):
        if origin_exit not in self.exits:
            self.error("Invalid origin (link) " + str(origin_exit))
            return False
        if dest_exit not in self.exits:
            self.error("Invalid destination (link) " + str(dest_exit))
            return False
        if self.exits[origin_exit][1] > 0 and origin_exit > 21:
            self.error("Origin already linked: " + str(origin_exit) + " " + str(self.exits[origin_exit]))
            return False
        if self.exits[dest_exit][2] > 0 and dest_exit > 21:
            self.error("Destination already linked: " + str(dest_exit) + " " + str(self.exits[dest_exit]))
            return False
        self.exits[origin_exit][1] = dest_exit
        self.exits[dest_exit][2] = origin_exit
        self.exit_log.append([origin_exit, dest_exit])
        self.verbose("   Linked " + str(origin_exit) + " " + str(self.exits[origin_exit][10]) + " - " + str(
            dest_exit) + " " + str(self.exits[dest_exit][10]))
        if update_graph and self.exits[origin_exit][5]:
            origin = self.exits[origin_exit][3]
            dest = self.exits[dest_exit][4]
            if dest not in self.graph[origin][1]:
                self.graph[origin][1].append(dest)
            self.new_connection(origin, dest, 0)
            if self.is_accessible(origin) and not self.is_accessible(dest):
                self.traverse([dest], test=False)
        if (origin_exit <= 21 or self.coupled_exits) and check_connections and self.is_exit_coupled(
                origin_exit) and self.is_exit_coupled(dest_exit):
            new_origin = self.exits[dest_exit][0]
            new_dest = self.exits[origin_exit][0]
            if new_origin <= 21:  # Boss exits
                if self.exits[new_origin][5]:
                    self.link_exits(new_origin, new_dest, False, update_graph)
            else:
                if self.exits[new_origin][1] != -1 or self.exits[new_dest][2] != -1:
                    self.error("Return exit already linked: " + str(new_origin) + " " + str(new_dest))
                    return False
                else:
                    self.link_exits(new_origin, new_dest, False, update_graph)
        return True

    # Unlinks two previously linked exits
    def unlink_exits(self, origin_exit, dest_exit, check_connections=True, update_graph=True):
        if origin_exit not in self.exits:
            self.error("Invalid origin (unlink) " + str(origin_exit))
            return False
        if dest_exit and dest_exit not in self.exits:
            self.error("Invalid destination (unlink) " + str(dest_exit))
            return False
        if dest_exit and (self.exits[origin_exit][1] != dest_exit or self.exits[dest_exit][2] != origin_exit):
            self.warn(
                "Attempted to unlink exits that are not correctly linked: " + str(origin_exit) + " " + str(dest_exit))
        if not dest_exit:
            dest_exit = origin_exit
        self.exits[origin_exit][1] = -1
        self.exits[dest_exit][2] = -1
        for x in self.exit_log:
            if x[0] == origin_exit:
                self.exit_log.remove(x)
        self.verbose("   Unlinked " + str(origin_exit) + " " + str(self.exits[origin_exit][10]) + " - " + str(
            dest_exit) + " " + str(self.exits[dest_exit][10]))
        if update_graph and self.exits[origin_exit][5]:
            origin = self.exits[origin_exit][3]
            dest = self.exits[dest_exit][4]
            if dest in self.graph[origin][1]:
                self.graph[origin][1].remove(dest)
            if dest in self.graph[origin][10]:
                self.graph[origin][10].remove(dest)
        if self.coupled_exits and check_connections and self.is_exit_coupled(origin_exit) and self.is_exit_coupled(
                dest_exit):
            new_origin = self.exits[dest_exit][0]
            new_dest = self.exits[origin_exit][0]
            self.unlink_exits(new_origin, new_dest, False, update_graph)
        if check_connections and update_graph:
            self.update_graph(True, True, True)
        return True

    # Bidirectional exit link. Make exit1 send the player to where exit2 is, and vice versa.
    def join_exits(self, exit1, exit2):
        return (self.link_exits(exit1, self.exits[exit2][0], False, False) and self.link_exits(exit2,
                                                                                               self.exits[exit1][0],
                                                                                               False, False))

    # Unlink both sides of a bidirectional exit.
    def unjoin_exit(self, exit):
        linked_exit = self.exits[exit][1]
        joined_exit = self.exits[self.exits[exit][0]][2]
        joined_linked_exit = self.exits[joined_exit][1]
        return (self.unlink_exits(exit, linked_exit, False, False) and self.unlink_exits(joined_exit,
                                                                                         joined_linked_exit, False,
                                                                                         False))

    # Append/insert bidirectional exits. Joins base_exit to new_exit1.
    # If base_exit was already joined, its former partner is joined to new_exit2.
    def insert_exit(self, base_exit, new_exit1, new_exit2=0):
        if any(x not in self.exits for x in [base_exit, new_exit1]) or (new_exit2 > 0 and new_exit2 not in self.exits):
            self.error("Can't insert nonexistent exit, one of: " + str(base_exit) + " " + str(new_exit1) + " " + str(
                new_exit2))
            return False
        if self.exits[new_exit1][1] > 0:
            self.error("Can't insert exit that's already joined: " + str(new_exit1))
            return False
        if self.exits[base_exit][1] < 0:  # Append.
            return self.join_exits(base_exit, new_exit1)
        else:  # Insert.
            if (new_exit2 == 0) or (self.exits[new_exit2][1] > 0):
                self.error("Can't insert nonexistent or joined exit: " + str(new_exit2))
                return False
            joined_exit = self.exits[self.exits[base_exit][0]][2]
            self.unjoin_exit(base_exit)
            return (self.join_exits(base_exit, new_exit1) and self.join_exits(joined_exit, new_exit2))

    def print_exit_log(self, exit_log=[]):
        for origin, dest in exit_log:
            self.verbose(str(self.exits[origin][10]) + " - " + str(self.exits[dest][10]))

    # Returns lists of origin exits and destination exits that open up new nodes
    def get_open_exits(self, check_progression=False):
        open_exits = [[], []]
        for node in self.graph:
            if not check_progression or self.is_accessible(node):
                for exit in self.graph[node][14]:
                    if self.exits[exit][1] == -1:
                        open_exits[0].append(exit)
            if not check_progression or not self.is_accessible(node):
                for exit in self.graph[node][15]:
                    if self.exits[exit][2] == -1:
                        open_exits[1].append(exit)
        return open_exits

    # Takes a list of origin and destination exits, returns a suitable match
    def find_exit(
        self, origin_exits_ls=[], dest_exits_ls=[], check_direction=False, check_progression=False,
        check_ds_access=False, test=False
    ):
        if not origin_exits_ls:
            self.verbose("  No more accessible exits available")
            return False
        elif not dest_exits_ls:
            self.verbose("  No destination exits available from " + str(origin_exits_ls))
            return False

        origin_exits = origin_exits_ls[:]
        dest_exits = dest_exits_ls[:]

        done = False
        quarantine_o = []
        while not done and origin_exits:
            origin_exit = 0
            while not origin_exit and origin_exits:
                origin_exit = origin_exits.pop(0)
                origin = self.exits[origin_exit][3]
                sister_exit = self.exits[origin_exit][0]
                if self.exits[origin_exit][1] != -1 or (check_progression and not self.is_accessible(origin)):
                    origin_exit = 0

            if not origin_exit:
                self.verbose("  No more accessible exits available")
                return False

            direction = self.exit_direction(origin_exit)
            dest_exit = 0
            quarantine_d = []
            while not done and dest_exits:
                try_link = False
                while not dest_exit and dest_exits:
                    dest_exit = dest_exits.pop(0)
                    dest = self.exits[dest_exit][4]
                    if self.exits[dest_exit][2] != -1 or not self.cmp_exit_pool(origin_exit, dest_exit) or (
                            check_progression and self.is_accessible(dest)):
                        dest_exit = 0

                if not dest_exit:
                    self.verbose("  No destination exits available from " + str(origin_exit))
                    return False

                direction_new = self.exit_direction(dest_exit)
                if dest_exit != sister_exit and (not check_direction or direction_new == direction):
                    try_link = True
                    if self.link_exits(origin_exit, dest_exit, self.coupled_exits, True):
                        if True:  # or not check_ds_access or self.check_ds_access(dest):
                            done = True
                            origin_final = origin_exit
                            dest_final = dest_exit

                if not done:
                    quarantine_d.append(dest_exit)
                    if try_link:
                        self.unlink_exits(origin_exit, dest_exit, True, True)
                    dest_exit = 0

            if not done:
                quarantine_o.append(origin_exit)
                dest_exits += quarantine_d
                quarantine_d.clear()

        if not done:
            self.verbose("No suitable links could be found - in quarantine: " + str(quarantine_o))
            return False

        # Clean up O/D lists
        origin_exits += quarantine_o
        for exit in origin_exits:
            if self.exits[exit][1] != -1:
                origin_exits.remove(exit)
        for exit in dest_exits:
            if self.exits[exit][2] != -1:
                dest_exits.remove(exit)

        return [origin_final, dest_final, origin_exits, dest_exits]

    # Check if player at origin could reach dest via open edges.
    def check_access(self, origin=-1, dest=-1, check_mutual=False, formless=False):
        if origin not in self.graph or dest not in self.graph:
            return False
        if self.graph[origin][7] or self.graph[dest][7]:
            return False
        success = False
        if origin == dest or (dest in self.graph[origin][10] and not formless):
            success = True
        elif formless:
            to_visit = [origin]
            visited = []
            while not success and to_visit:
                node = to_visit.pop()
                visited.append(node)
                if self.graph[node][7]:  # Will-Only nodes don't propagate formless access
                    continue
                elif node == dest:
                    success = True
                    break
                else:
                    to_visit.extend([n for n in self.graph[node][1] if n not in visited + to_visit])
                    for edge in self.graph[node][12]:
                        if (self.logic[edge][0] > 0) and self.edge_formless(edge) and (
                                self.logic[edge][2] not in visited + to_visit):
                            to_visit.append(self.logic[edge][2])
        else:
            to_visit = self.graph[origin][10][:]
            visited = [origin]
            while not success and to_visit:
                node = to_visit.pop(0)
                visited.append(node)
                if not self.graph[node][7] and dest in self.graph[node][10]:
                    success = True
                else:
                    for x in self.graph[node][10]:
                        if x not in to_visit + visited:
                            to_visit.append(x)
        if not check_mutual or not success:
            return success
        return self.check_access(dest, origin, False, formless)

    # Build islands, i.e. groups of nodes accessible from each other, generally assuming all progression.
    # With require_mutual, island nodes are mutually accessible, with no one-way drops or similar.
    # Examples: Freejia-Exterior; north half of Sky Garden SW Top.
    def build_islands(self, require_mutual=True):
        islands = [[] for _ in range(13)]
        visited = []
        start_island = []
        for node in self.graph:
            if node not in visited and self.graph[node][2]:
                to_visit = [node]
                new_nodes = []
                origin_exits = []
                dest_exits = []
                origin_logic = []
                dest_logic = []
                is_start = False
                dungeon = 9999
                while to_visit:
                    x = to_visit.pop(0)
                    visited.append(x)
                    new_nodes.append(x)
                    if 0 in self.graph[x][8]:
                        is_start = True
                    for exit in self.graph[x][14]:
                        if self.exits[exit][1] == -1:
                            origin_exits.append(exit)
                            dungeon = min(dungeon, self.exit_dungeon(exit))
                    for exit in self.graph[x][15]:
                        if self.exits[exit][2] == -1:
                            dest_exits.append(exit)
                    for edge in self.graph[x][12]:
                        if self.logic[edge][0] == 0:
                            origin_logic.append(edge)
                    for edge in self.graph[x][13]:
                        if self.logic[edge][0] == 0:
                            dest_logic.append(edge)
                    for y in self.graph[x][10]:
                        if y not in visited + to_visit and self.check_access(x, y, require_mutual):
                            to_visit.append(y)
                    if not require_mutual:
                        for y in self.graph[x][8]:
                            if y not in visited + to_visit and self.check_access(y, x, False):
                                to_visit.append(y)
                island = [new_nodes, origin_exits, dest_exits, origin_logic, dest_logic]
                if is_start:
                    start_island = island
                if dungeon == 9999 or not self.dungeon_shuffle:
                    dungeon = 0
                islands[dungeon].append(island)

        return [start_island, islands]

    def exit_dungeon(self, exit=-1):
        if exit not in self.exits:
            self.error("Exit not in database")
            return -1
        if self.dungeon_shuffle:  # == "Chaos":
            return 1
        return self.exits[exit][8]

    def check_dungeon(self, exit1=-1, exit2=-1):
        if exit1 not in self.exits or exit2 not in self.exits:
            self.error("Exit not in database")
            return -1
        if self.exit_dungeon(exit1) != self.exit_dungeon(exit2):
            return False
        return True

    # Returns the (arbitrary) ID of the pool an exit should be shuffled in, or -1 if not shuffled.
    def get_exit_pool(self, exit):
        if (exit not in self.exits) or not self.entrance_shuffle:
            return -1
        dungeon = self.exits[exit][8]
        pooltype = self.exits[exit][9]
        if self.town_shuffle and (pooltype == 1):
            return 1
        if self.dungeon_shuffle and (pooltype > 1) and (dungeon > 0):
            return 2
        return -1

    # Returns whether two exits are pooled for shuffling.
    def cmp_exit_pool(self, exit1, exit2):
        return (self.get_exit_pool(exit1) == self.get_exit_pool(exit2))

    def shuffle_chaos_dungeon(self):
        # Build dungeon node islands for the skeleton, assuming free and all-form movement
        self.reset_progress(True)
        self.items_collected = [800,802,803]+self.list_typed_items(types=[1, 2, 4, 5], shuffled_only=False, incl_placed=True)
        for removed_orb in [707,708,709,735]:   # Due to awkward orb placement, treat Inca exterior and Wat Outer South as corridors
            if removed_orb in self.items_collected:
                self.items_collected.remove(removed_orb)
        for node in self.graph:
            self.graph[node][0] = True
            self.graph[node][4] = 0x37
        self.update_graph(True, False, True)
        island_result = self.build_islands()
        islands = island_result[1].pop(1)  # pop(1) = list of all islands assigned to the chaos dungeon
        # An island is: [ [nodes], [origin_exits], [dest_exits], [origin_logic], [dest_logic] ].
        # For dungeon construction, we want islands grouped by count of dungeon-internal exits.
        dungeon_exit_keys = [exit for exit in self.exits if self.exits[exit][9] == 3]
        deadend_islands = []
        corridor_islands = []
        free_ds_corridor_islands = []
        branch_islands = []
        foyer_islands = []
        random.shuffle(islands)
        for island in islands:
            internal_exits = [exit for exit in island[1] if self.exits[exit][9] == 2 and self.is_exit_coupled(exit)]
            if not internal_exits:
                continue
            random.shuffle(internal_exits)
            for exit in internal_exits:
                dungeon_exit_keys.append(exit)
            subisland = [island[0][:], internal_exits, []]  # [nodes, unmapped-exits, mapped-exits]
            if any(region in subisland[0] for region in [170, 212, 413]):  # SkGn, Mu, and Pymd have branching foyers
                foyer_islands.append(subisland)
            elif len(subisland[1]) == 1:
                deadend_islands.append(subisland)
            elif len(subisland[1]) == 2:
                is_free_ds_corridor = False
                ds_node = next((n for n in subisland[0] if n in self.ds_nodes), 0)
                if ds_node > 0:  # Island contains a DS node
                    ds_loc = next(loc for loc in self.graph[ds_node][11] if self.item_locations[loc][1] == 2)
                    if self.spawn_locations[ds_loc][3]:  # Island DS allows transform
                        if all(self.edge_formless(e) for n in subisland[0] for e in self.graph[n][12]):   # Island is internally-formless
                            is_free_ds_corridor = True
                if is_free_ds_corridor:
                    free_ds_corridor_islands.append(subisland)
                else:
                    corridor_islands.append(subisland)
            else:
                branch_islands.append(subisland)
        # At this point a "deadend" may be the bottom or top of a ledge, or behind or in front of a button.
        # Such one-way exits are functionally part of a corridor or branch, except that the low/back exit
        # can't be appended to an opening to grow the dungeon.
        # So, we coalesce the islands by one-way accessibility, keeping track of the "blocked" exits.
        blocked_exits = []
        merged_islands_for_deletion = []
        all_islands = deadend_islands + corridor_islands + branch_islands
        for lower_i in deadend_islands:
            lower_n = lower_i[0][0]
            lower_map = self.graph[lower_n][3][3]  # One-way access must be within the same map
            upper_i = next((i for i in all_islands if i != lower_i and any((lower_map == self.graph[upper_n][3][3]) and self.check_access(upper_n,lower_n,False) for upper_n in i[0])), [])
            if upper_i:  # Merge the lower island into the upper one, and record the lower exit
                upper_i[0].extend(lower_i[0][:])
                upper_i[1].extend(lower_i[1][:])
                blocked_exits.extend(lower_i[1][:])
                merged_islands_for_deletion.append(lower_i)
        for island in merged_islands_for_deletion:  # Removed merged deadends
            deadend_islands.remove(island)
        for exit in blocked_exits:  # If any islands grew, move them to the correct list
            grown_island = next(i for i in deadend_islands + corridor_islands + branch_islands if exit in i[1])
            if grown_island in deadend_islands and len(grown_island[1]) > 1:
                deadend_islands.remove(grown_island)
                if len(grown_island[1]) == 2:
                    corridor_islands.append(grown_island)
                else:
                    branch_islands.append(grown_island)
            elif grown_island in corridor_islands and len(grown_island[1]) > 2:
                corridor_islands.remove(grown_island)
                branch_islands.append(grown_island)
        # Various special exits that aren't detected programmatically: 72 back of EdDg, 126 behind D.Block, 234 Mine behind fences,
        # 293/295/305 SkGn SE behind robot / SW behind N pegs / NW behind statue, 534/538 Kress behind drops 1/2.
        blocked_exits.extend([72, 126, 234, 293, 295, 305, 534, 538])
        # Append non-oneway (=non-blocked), non-IncaExt, non-WatOuterS corridors to SkGn, Pymd, and Mu foyers, so they're not boring
        oneway_corridor_islands = [i for i in corridor_islands if any(x in blocked_exits for x in i[1])]
        random.shuffle(corridor_islands)
        elig_foyer_corridors = [i for i in corridor_islands if i not in oneway_corridor_islands and not any(
            self.graph[n][3][3] in [0x1d, 0xb1] for n in i[0])]
        # Pyramid is done first and given non-DS corridors; thus Mu and SkGn have increased DS corridor odds
        for base_island in sorted(foyer_islands, key=lambda i: max(self.graph[n][3][3] for n in i[0]), reverse=True):
            is_pymd_island = any(self.graph[n][3][3] == 204 for n in base_island[0])
            foyer_exits = base_island[1][:]
            for base_exit in foyer_exits:
                if is_pymd_island:
                    new_corridor = next(i for i in elig_foyer_corridors if not any(
                        self.item_locations[loc][1] == 2 for n in i[0] for loc in self.graph[n][11]))
                else:
                    new_corridor = next(i for i in elig_foyer_corridors)
                elig_foyer_corridors.remove(new_corridor)
                corridor_islands.remove(new_corridor)
                corridor_exit = new_corridor[1].pop()
                base_island[1].remove(base_exit)
                self.join_exits(corridor_exit, base_exit)
                # The corridor is absorbed into the foyer, and the exits between them are forgotten
                base_island[0].extend(new_corridor[0])
                base_island[1].extend(new_corridor[1])
        # Promote a random Will-traversable branch to a foyer for dungeons that don't have a branching foyer
        random.shuffle(branch_islands)
        for exit in [x for x in self.exits if self.exits[x][9] == 3]:
            new_foyer_island = next(
                (i for i in branch_islands if all((edef[3] & 0x21) for edef in self.logic.values() if edef[1] in i[0])),
                [])
            if new_foyer_island:
                branch_islands.remove(new_foyer_island)
            else:  # Accept any island if there are no fully-Will-traversable ones
                new_foyer_island = branch_islands.pop()
            new_entr = next(x for x in new_foyer_island[1] if x not in blocked_exits)
            new_foyer_island[1].remove(new_entr)
            new_foyer_island[2].append(new_entr)
            self.join_exits(exit, new_entr)
            foyer_islands.append(new_foyer_island)
        # The foyers are our nascent (as-yet-unconnected) skeleton;
        # also, save off node sets so we can swap islands for formful access fixes later
        skeleton = foyer_islands
        deadend_nodesets = []
        corridor_nodesets = []
        branch_nodesets = []
        foyer_nodesets = []
        for island in deadend_islands:
            deadend_nodesets.append(island[0][:])
        for island in corridor_islands:
            corridor_nodesets.append(island[0][:])
        for island in branch_islands:
            branch_nodesets.append(island[0][:])
        for island in foyer_islands:
            foyer_nodesets.append(island[0][:])
        # Append all branches and one-way corridors, then append deadends to all openings.
        while branch_islands + oneway_corridor_islands + deadend_islands and any(
                len(island[1]) > 0 for island in skeleton):
            random.shuffle(skeleton)
            if branch_islands + oneway_corridor_islands:
                if (not oneway_corridor_islands) or (branch_islands and (random.randint(0, 1) == 1)):
                    new_island = branch_islands.pop()
                else:
                    new_island = oneway_corridor_islands.pop()
                    corridor_islands.remove(new_island)
            else:  # Deadends are the last type appended
                new_island = deadend_islands.pop()
            new_exit = next(exit for exit in new_island[1] if exit not in blocked_exits)
            new_island[1].remove(new_exit)
            new_island[2].append(new_exit)
            base_island = next(island for island in skeleton if len(island[1]) > 0)
            skeleton.remove(base_island)
            base_exit = base_island[1].pop()
            base_island[2].append(base_exit)
            skeleton.append(new_island)
            skeleton.append(base_island)
            self.join_exits(base_exit, new_exit)
        # Calculate how many loops we need to create
        num_deadends = len(deadend_islands)
        num_openings = 0
        for island in skeleton:
            num_openings += len(island[1])
        if (num_deadends - num_openings) % 2 == 1:
            # Discard one deadend (442) and one Nothing to match parity of deadends to openings
            # (though I don't think this state is possible in IOG if the above code works)
            if any(442 in x[0] for x in skeleton):
                discard_island = next(x for x in skeleton if 442 in x[0])
                skeleton.remove(discard_island)
                joined_exit = self.exits[self.exits[641][0]][2]
                joined_island = next(x for x in skeleton if joined_exit in x[2])
                joined_island[2].remove(joined_exit)
                joined_island[1].append(joined_exit)
                self.unjoin_exit(641)
                num_openings += 1
            else:
                discard_island = next(x for x in deadend_islands if 442 in x[0])
                deadend_islands.remove(discard_island)
                num_deadends -= 1
            self.item_pool[0][0] -= 1
            self.item_locations[132][2] = True
            self.item_locations[132][3] = 0
            self.item_locations[132][7] = 0
            self.optional_nodes.append(442)
            self.link_exits(641, self.exits[641][0], False, False)
        if num_deadends > num_openings:
            self.error("Not enough dungeon exits: need " + str(num_deadends - num_openings) + " more")
            return False
        elif num_deadends < num_openings:
            # Create loops by connecting openings with corridors
            remaining_inserts = (num_openings - num_deadends) / 2
            random.shuffle(skeleton)
            random.shuffle(corridor_islands)
            while remaining_inserts:
                loop_island1 = next(x for x in skeleton if len(x[1]) > 0)
                skeleton.remove(loop_island1)
                loop_island2 = next((x for x in skeleton if len(x[1]) > 0), loop_island1)
                # Allow for the case where one island remains and has 2 open exits
                if loop_island2 != loop_island1:
                    skeleton.remove(loop_island2)
                corridor_island = corridor_islands.pop()
                loop_exit1 = loop_island1[1].pop()
                loop_exit2 = loop_island2[1].pop()
                corridor_exit1 = corridor_island[1].pop()
                corridor_exit2 = corridor_island[1].pop()
                corridor_island[2].append(corridor_exit1)
                corridor_island[2].append(corridor_exit2)
                self.join_exits(loop_exit1, corridor_exit1)
                self.join_exits(loop_exit2, corridor_exit2)
                loop_island1[2].append(loop_exit1)
                loop_island2[2].append(loop_exit2)
                skeleton.append(loop_island1)
                if loop_island2 != loop_island1:
                    skeleton.append(loop_island2)
                skeleton.append(corridor_island)
                remaining_inserts -= 1
        # Insert corridors randomly
        while corridor_islands:
            random.shuffle(skeleton)
            random.shuffle(dungeon_exit_keys)
            new_island = corridor_islands.pop()
            new_exit1 = new_island[1].pop()
            new_exit2 = new_island[1].pop()
            new_island[2].append(new_exit1)
            new_island[2].append(new_exit2)
            base_exit = next(
                x for x in dungeon_exit_keys if self.exits[x][1] > 0 and any(x in island[2] for island in skeleton))
            base_island = next(island for island in skeleton if base_exit in island[2])
            self.insert_exit(base_exit, new_exit1, new_exit2)
            skeleton.append(new_island)
        # Assuming all DSes are for transform, find and fix missing formful access if possible.
        # Need to reset and re-traverse in every iteration, because we're moving exits around.
        graph_free_access = {n: self.graph[n][1][:] for n in self.graph}
        node_to_fix = 0
        nodes_fixed = [node_to_fix]
        f_missing_nodes = {-1}
        while free_ds_corridor_islands:
            random.shuffle(dungeon_exit_keys)
            self.reset_progress(True)
            for n in self.graph:
                self.graph[n][1] = graph_free_access[n][:]
            self.items_collected = [800,802,803]+self.list_typed_items(types=[1, 2, 4, 5], shuffled_only=False, incl_placed=True)
            for loc in self.spawn_locations:
                if self.spawn_locations[loc][3] and loc in self.item_locations and self.item_locations[loc][1] == 2:
                    self.item_locations[loc][2] = True
            self.update_graph(True, True, True)
            for s in foyer_nodesets:
                for n in s:
                    self.graph[n][4] = 0x11  # Will can access all foyers
            trav_nodes = self.traverse(to_visit=[n for s in foyer_nodesets for n in s])
            f_missing_nodes = {self.logic[e][1] for e in self.open_edges if
                               not self.edge_formless(e) and any(self.logic[e][1] in i[0] for i in skeleton) and not (
                                       self.logic[e][3] & self.graph[self.logic[e][1]][
                                   4]) and not self.is_accessible(self.logic[e][2])}
            if not f_missing_nodes:
                break  # Success
            elif any(node in f_missing_nodes for node in nodes_fixed):
                break  # Failed to get consistent DS access for a node; return the dungeon as-is and let the caller figure it out or fail
            node_to_fix = f_missing_nodes.pop()
            nodes_fixed.append(node_to_fix)
            island_to_fix = next(i for i in skeleton if node_to_fix in i[0])
            new_island = free_ds_corridor_islands.pop()
            base_exit = next((x for x in dungeon_exit_keys if
                              self.graph[self.exits[x][3]][0] and not self.graph[self.exits[x][3]][9] and x not in
                              island_to_fix[2] and self.check_access(self.exits[x][3], node_to_fix, False, True)),
                             island_to_fix[2][0])
            new_exit1 = new_island[1].pop()
            new_exit2 = new_island[1].pop()
            new_island[2].extend([new_exit1, new_exit2])
            self.insert_exit(base_exit, new_exit1, new_exit2)
        # Insert any remaining free DS corridors
        while free_ds_corridor_islands:
            random.shuffle(skeleton)
            random.shuffle(dungeon_exit_keys)
            new_island = free_ds_corridor_islands.pop()
            new_exit1 = new_island[1].pop()
            new_exit2 = new_island[1].pop()
            new_island[2].append(new_exit1)
            new_island[2].append(new_exit2)
            base_exit = next(
                x for x in dungeon_exit_keys if self.exits[x][1] > 0 and any(x in island[2] for island in skeleton))
            base_island = next(island for island in skeleton if base_exit in island[2])
            self.insert_exit(base_exit, new_exit1, new_exit2)
            skeleton.append(new_island)
        # Clean up the graph
        self.reset_progress(True)
        for n in self.graph:
            self.graph[n][1] = graph_free_access[n][:]
        for loc in self.spawn_locations:
            if self.spawn_locations[loc][3] and loc in self.item_locations and self.item_locations[loc][1] == 2 and self.item_locations[loc][3] == 0:
                self.item_locations[loc][2] = False

    # Entrance randomizer
    def shuffle_exits(self):
        # Map passages and all fixed exits to graph.
        one_way_exits = []
        for x in self.exits:
            if self.exits[x][1] < 0:
                if not self.is_exit_coupled(x):
                    one_way_exits.append(x)
                self.graph[self.exits[x][3]][14].append(x)
                self.graph[self.exits[x][4]][15].append(x)

        # Special case for Slider exits in Angel Dungeon
        if self.dungeon_shuffle:  # != "None":
            if random.randint(0, 1):
                self.link_exits(408, 414, False)
                self.link_exits(409, 415, False)
                self.link_exits(414, 408, False)
                self.link_exits(415, 409, False)
            else:
                self.link_exits(408, 408, False)
                self.link_exits(409, 409, False)
                self.link_exits(414, 414, False)
                self.link_exits(415, 415, False)

        # If using a coupled shuffle, map one-way exits to one-way dests
        exit_log = []
        if self.coupled_exits:
            one_way_dest = one_way_exits[:]
            random.shuffle(one_way_dest)
            while one_way_exits:
                o_exit = one_way_exits.pop()
                found_oneway = False
                while not found_oneway:
                    d_exit = one_way_dest.pop()
                    if self.cmp_exit_pool(o_exit, d_exit):
                        self.link_exits(o_exit, d_exit, False)
                        exit_log.append([o_exit, d_exit])
                        found_oneway = True
                    else:
                        one_way_dest.append(d_exit)
                        random.shuffle(one_way_dest)
            self.info("One-way exits mapped")

        # Coupled dungeon shuffles need special handling
        if self.dungeon_shuffle and self.coupled_exits:
            if self.dungeon_shuffle:  # == "Chaos":
                # Link Pyramid room-pairs as in vanilla, reducing Pymd corridor count from 13 to 6.
                dc_exits_within_pyramid_rooms = [638, 644, 650, 656, 658, 664, 670]
                for exitnum in dc_exits_within_pyramid_rooms:
                    self.join_exits(exitnum, self.exits[exitnum][0])
                self.shuffle_chaos_dungeon()
            self.info("Dungeon shuffle complete")
        # Clean up dungeon shuffle artificial edges
        self.delete_objects(items=[800], with_close=True)
        self.delete_objects(items=[801], with_close=False)

        if self.dungeon_shuffle and self.coupled_exits and not self.town_shuffle:
            return True

        # Assume all items and abilities
        self.info("Beginning exit shuffle...")
        self.reset_progress(True)
        self.items_collected = self.list_typed_items(types=[1, 2, 4, 5], shuffled_only=True, incl_placed=True)
        self.update_graph(True, True, True)

        # Build world skeleton with islands
        self.unsolve()
        island_result = self.build_islands()
        islands = island_result[1].pop(0)  # pop(0) = all non-dungeon islands

        traverse_result = self.traverse()
        visited = traverse_result[0]
        origin_exits = []
        for node in visited:
            origin_exits += self.graph[node][14]

        i = 0
        for x in islands:
            i += 1
            self.verbose("Initial island " + str(i) + " (" + str(x[1]) + "," + str(x[2]) + "):")
            for y in x[0]:
                self.verbose(" - " + self.graph[y][5])
        self.info(" Joining initial islands...")

        check_direction = True
        check_progression = True
        quarantine = []
        while islands:
            random.shuffle(islands)
            island = islands.pop(0)
            nodes_new = island[0]
            origin_exits_new = island[1]
            dest_exits_new = island[2]

            if not dest_exits_new or not origin_exits_new or self.is_accessible(nodes_new[0]):
                pass
            else:
                if (check_progression and not origin_exits_new) or (
                        self.coupled_exits and (len(origin_exits_new) < 2 or len(dest_exits_new) < 2)):
                    quarantine.append(island)
                else:
                    random.shuffle(origin_exits)
                    random.shuffle(dest_exits_new)

                    result = self.find_exit(origin_exits, dest_exits_new, check_direction, True)
                    if not result:
                        quarantine.append(island)
                    else:
                        self.verbose("New island:")
                        for y in nodes_new:
                            self.verbose(" - " + str(self.graph[y][5]))
                        traverse_result = self.traverse(island[0])
                        visited += traverse_result[0]
                        progression_result = self.get_open_exits()
                        origin_exits = progression_result[0]
                        check_direction = True

            if not islands:
                if check_direction:
                    check_direction = False
                    islands += quarantine
                    quarantine.clear()
                elif check_progression:
                    check_progression = False
                    check_direction = True
                    islands += quarantine
                    quarantine.clear()
            if not islands and island_result[1]:
                islands = island_result[1].pop(0)
                check_direction = True
                check_progression = True
                quarantine = []

        self.info(" Island construction complete")

        # Check Dark Space access, map exits accordingly
        self.reset_progress()
        self.items_collected = self.list_typed_items(types=[1, 2, 4, 5], shuffled_only=True, incl_placed=True)
        self.update_graph(True, True, True)

        island_result = self.build_islands()
        islands = island_result[1].pop(0)

        islands_no_ds = []
        ds_check_visited = []
        for island in islands:
            if self.is_accessible(island[0][0]) and not self.check_ds_access(island[0][0], False, True,
                                                                             ds_check_visited):
                islands_no_ds.append(island)

        if islands_no_ds:
            self.verbose("Islands with no DS access:")
            i = 0
            for x in islands_no_ds:
                i += 1
                self.verbose("Island " + str(x))
                for y in x[0]:
                    self.verbose("- " + str(self.graph[y][5]))

            dest_exits_ds = []
            for node in self.graph:
                if node not in visited and self.check_ds_access(node, False, True, ds_check_visited):
                    for exit in self.graph[node][15]:
                        if self.exits[exit][2] == -1:
                            dest_exits_ds.append(exit)

            while islands_no_ds:
                island = islands_no_ds.pop(0)
                result = self.find_exit(island[1], dest_exits_ds, check_direction)
                if not result:
                    self.error("Could not find Dark Space access")
                    return False
                else:
                    dest_exits_ds = result[3]

        self.info(" Dark Space access check successful")

        # Link exits forward
        self.reset_progress()
        self.items_collected = self.list_typed_items(types=[1, 2, 4, 5], shuffled_only=True, incl_placed=True)
        self.update_graph(True, True, True)
        self.traverse()

        check_progression = True
        check_direction = True
        while origin_exits:
            progression_result = self.get_open_exits(check_progression)
            origin_exits = progression_result[0]
            dest_exits = progression_result[1]
            random.shuffle(origin_exits)
            random.shuffle(dest_exits)
            if origin_exits:
                result = self.find_exit(origin_exits, dest_exits, check_direction, check_progression, True, False)
                if result:
                    origin_exit = result[0]
                    dest_exit = result[1]
                    dest = self.exits[dest_exit][4]
                    self.traverse([dest])
                elif check_direction:
                    check_direction = False
                elif check_progression:
                    check_progression = False
                    check_direction = True
                    self.info("  Finished mapping progression exits")
                else:
                    self.info("Can't link any origin exit of " + str(origin_exits) + " to any dest exit of " + str(
                        dest_exits))
                    return False

        # Randomly link any leftover exits
        origin_exits = []
        dest_exits = []
        for exit in self.exits:
            if self.exits[exit][1] == -1:
                self.verbose(" Unmapped exit: " + str(exit) + " " + str(self.exits[exit]))
                origin_exits.append(exit)
            if self.exits[exit][2] == -1:
                self.verbose(" No exit mapped to: " + str(exit) + " " + str(self.exits[exit]))
                dest_exits.append(exit)
            if origin_exits:
                random.shuffle(origin_exits)
            if dest_exits:
                random.shuffle(dest_exits)

        while origin_exits:
            origin_exit = origin_exits.pop(0)
            if not dest_exits:
                self.error("Entrance rando failed: bad exit parity")
                return False
            candidate_dest_exit_idx = 0
            fallback_dest_exit_idx = -1
            while candidate_dest_exit_idx < len(dest_exits) - 1:
                candidate_dest_exit = dest_exits[candidate_dest_exit_idx]
                # Prefer mapping to an exit other than itself in the same pool.
                if self.cmp_exit_pool(origin_exit, candidate_dest_exit):
                    if candidate_dest_exit == self.exits[origin_exit][0]:
                        fallback_dest_exit_idx = candidate_dest_exit_idx
                    else:  # If we get here, candidate_dest_exit_idx meets both criteria, so use it.
                        fallback_dest_exit_idx = -1
                        break
                candidate_dest_exit_idx += 1
            if fallback_dest_exit_idx > -1:
                dest_exit = dest_exits.pop(fallback_dest_exit_idx)
            else:
                dest_exit = dest_exits.pop(candidate_dest_exit_idx)
            self.link_exits(origin_exit, dest_exit, False)
            if self.coupled_exits and origin_exit != self.exits[dest_exit][0]:  # Map reverse direction.
                self.link_exits(self.exits[dest_exit][0], self.exits[origin_exit][0], False)
                origin_exits.remove(self.exits[dest_exit][0])
                dest_exits.remove(self.exits[origin_exit][0])

        self.info("Entrance rando successful")

        return True

    def initialize_ds(self):
        # Clear DS access data from graph
        for x in self.graph:
            self.graph[x][4] = 0
            self.graph[x][9].clear()
        # Find nodes that contain Dark Spaces, and of those, which allow transform and don't contain an ability
        self.ds_locations = [loc for loc in self.spawn_locations if loc in self.item_locations]
        self.ds_nodes = [self.item_locations[loc][0] for loc in self.ds_locations]
        # Transform DSes are marked "filled" but contain item 0
        self.txform_locations = [loc for loc in self.ds_locations if self.spawn_locations[loc][3] and self.item_locations[loc][2] and not self.item_locations[loc][3]]
        self.txform_nodes = [self.item_locations[loc][0] for loc in self.txform_locations]
        return True

    # Translates logic and exits to world graph
    def update_graph(self, update_logic=True, update_ds=True, update_exits=False):
        self.info("Updating graph...")
        if update_exits:
            for exit in self.exits:
                if exit > 21 or self.exits[exit][5]:
                    # Check if exit has been shuffled
                    if self.exits[exit][1] > 0:
                        new_exit = self.exits[exit][1]
                    elif self.exits[exit][1] == 0:
                        new_exit = exit
                    else:
                        new_exit = -1
                    # Get exit origin
                    if new_exit > 0:
                        origin = self.exits[exit][3]
                        if not origin and self.is_exit_coupled(exit):
                            sister_exit = self.exits[exit][0]
                            origin = self.exits[sister_exit][4]
                            self.exits[exit][3] = origin
                        # Get (new) exit destination
                        if self.exits[new_exit][2] == 0 or self.exits[new_exit][2] == exit:
                            dest = self.exits[new_exit][4]
                            if not dest and self.is_exit_coupled(new_exit):
                                sister_exit = self.exits[new_exit][0]
                                dest = self.exits[sister_exit][3]
                                self.exits[new_exit][4] = dest
                            # Translate link into world graph
                            if origin and dest and (dest not in self.graph[origin][1]):
                                self.graph[origin][1].append(dest)
            self.verbose(" Graph exits updated")

        # Update logic edges that aren't form-specific
        if update_logic:
            for edge in self.logic:
                if self.edge_formless(edge):
                    self.check_edge(edge, [], True, self.graph[self.logic[edge][1]][4])
            self.verbose(" Graph formless logic updated")

        for node in self.graph:
            for x in self.graph[node][1]:
                if x not in self.graph[node][10]:
                    self.graph[node][10].append(x)
            for y in self.graph[node][10]:
                if node not in self.graph[y][8]:
                    self.graph[y][8].append(node)
            for z in self.graph[node][8]:
                if node not in self.graph[z][10]:
                    self.graph[z][10].append(node)
        self.verbose(" Graph node-node connections updated")

        if update_ds:
            # Clear and recalculate DS access for all nodes (recursively from DS nodes)
            self.initialize_ds()
            for node in self.ds_nodes:
                for loc in self.graph[node][11]:
                    if loc in self.spawn_locations and self.spawn_locations[loc][3]:
                        self.update_ds_access([node],0x20,[node])   # Propagate "reachable formlessly from a possibly-txform DS"
                if self.graph[node][0]:   # Only actually-visited nodes count for these flags
                    self.update_ds_access([node],0x10,[])   # Propagate "can traverse to a DS"
                    if node in self.txform_nodes:
                        self.update_ds_access([node],(0x01|0x02|0x04),[])   # Propagate form traversal
            self.update_ds_access([0],0x01,[])   # Will has access to the start node
            for node in [10,11,12,13,14]:   # Will has access to traversed overworld-connected nodes
                if self.graph[node][0]:
                    self.update_ds_access([node], 0x01, [])
            self.verbose(" Graph DS access updated")

        # Update form-specific logic, repeatedly until access stops growing
        if update_logic:
            all_f_edges = [e for e in self.logic if not self.edge_formless(e)]
            checked_f_edges = []
            checked_new_edge = True
            while checked_new_edge:
                checked_new_edge = False
                for edge in all_f_edges:
                    if edge not in checked_f_edges and self.check_edge(edge, [], True,
                                                                       self.graph[self.logic[edge][1]][4]):
                        checked_f_edges.append(edge)
                        checked_new_edge = True
            self.verbose(" Graph formful logic updated")

        return True

    # Return (bool) whether an edge is form-specific
    def edge_formless(self, edge):
        return (False or (self.logic[edge][3] & (0x20)) or (self.logic[edge][3] == 0))

    # Check whether a node's DS access data needs to be updated
    def consider_ds_node(self, node, access_mode, ds_nodes):
        if access_mode not in [0x01, 0x02, 0x04, 0x10, 0x20]:  # --then it's a combined access mode
            result = False
            for flag in [0x01, 0x02, 0x04, 0x10, 0x20]:
                if access_mode & flag:
                    result |= self.consider_ds_node(node, flag, ds_nodes)
            return result
        if access_mode in [0x02, 0x04, 0x20] and self.graph[node][7]:
            return False  # Always-Will nodes never allow not-Will or formless traversal
        if access_mode == 0x20 and any(ds_node not in self.graph[node][9] for ds_node in ds_nodes):
            return True
        if not (self.graph[node][4] & access_mode):
            return True
        return False

    # Check if start_node can reach a DS or be reached by a form
    def check_ds_access(self, start_node, access_mode, do_recurse, visited):
        if access_mode not in [0x01, 0x02, 0x04, 0x10, 0x20]:  # If combined access is checked, "or" logic is used
            for flag in [0x01, 0x02, 0x04, 0x10, 0x20]:
                sub_visited = visited[:]
                if (access_mode & flag) and self.check_ds_access(start_node, flag, do_recurse, sub_visited):
                    return True
            return False
        if start_node not in self.graph or start_node < 0:
            return False  # Not a real node, dude
        if self.graph[start_node][7] and access_mode in [0x02, 0x04, 0x20]:
            return False  # ForceWillForm denies non-Will and formless access
        if self.graph[start_node][4] & access_mode:
            return True  # Node has already been evaluated to have the right DS access
        if not do_recurse:
            return False  # Caller only wants to check this node's evaluated access
        if start_node in visited:
            return False  # We've already recursed through this node
        to_visit = [start_node]
        while to_visit:
            node = to_visit.pop(0)
            if node not in visited + [start_node] and self.check_ds_access(node, access_mode, do_recurse, visited):
                self.verbose("Node "+str(start_node)+" has form "+str(access_mode)+" access via node "+str(node))
                return True
            else:
                if node not in visited:
                    visited.append(node)
                if access_mode in [0x01, 0x02, 0x04,
                                   0x20]:  # if checking "can be reached [by form]", find nodes that can reach here
                    to_visit.extend([n for n in self.graph if node in self.graph[n][1] and n not in visited + to_visit])
                    for edge in self.graph[node][13]:
                        if (self.logic[edge][0] > 0) and (self.logic[edge][3] & access_mode) and (
                                self.logic[edge][1] not in visited + to_visit):
                            to_visit.append(self.logic[edge][1])
                else:  # if checking "can reach any DS", follow edges forward
                    to_visit.extend([n for n in self.graph[node][1] if n not in visited + to_visit])
                    for edge in self.graph[node][12]:
                        if (self.logic[edge][0] > 0) and ((self.logic[edge][3] & 0x07) == 0x07) and (
                                self.logic[edge][2] not in visited + to_visit):
                            to_visit.append(self.logic[edge][2])
        return False

    # Update DS access data for nodes, recursively to all connected nodes
    def update_ds_access(self, nodes, access_mode, ds_nodes):
        if not nodes:
            return True
        visit_forward = [[], [], [], []]  # visit for w, f, s, formless
        visit_reverse = []
        for node in nodes:
            self.graph[node][4] |= access_mode
            if access_mode & 0x10:  # Can reach a DS here, so propagate "can reach DS" backward
                visit_reverse = [x for x in self.graph[node][8] if self.consider_ds_node(x, 0x10, [])]
            if access_mode & (0x01 | 0x02 | 0x04 | 0x20):  # Can be transformed here, so propagate the form forward
                if access_mode & 0x20:
                    self.graph[node][9].extend([ds_node for ds_node in ds_nodes if ds_node not in self.graph[node][9]])
                for idx, flag in [(0, 0x01), (1, 0x02), (2, 0x04), (3, 0x20)]:
                    if (access_mode & flag):
                        visit_forward[idx].extend(
                            [n for n in self.graph[node][1] if self.consider_ds_node(n, flag, ds_nodes)])
                        for forward_edge in self.graph[node][12]:
                            if self.check_edge(forward_edge,[],False,flag) and self.consider_ds_node(self.logic[forward_edge][2],flag,ds_nodes) and self.logic[forward_edge][2] not in visit_forward[idx]:
                                visit_forward[idx].append(self.logic[forward_edge][2])
        result = self.update_ds_access(visit_reverse, 0x10, [])
        for idx, flag in [(0, 0x01), (1, 0x02), (2, 0x04)]:
            if visit_forward[idx]:
                result |= self.update_ds_access(set(visit_forward[idx]), flag, [])
        if visit_forward[3]:
            result |= self.update_ds_access(set(visit_forward[3]), 0x20, ds_nodes)
        return result

    # Check whether edge requirements are met by self.items_collected + items.
    # If update_graph, also connects the nodes in self.graph and propagates DS access.
    def check_edge(self, edge, items=[], update_graph=True, form=0xff):
        success = False
        if not (self.logic[edge][3] & form):
            return False
        elif self.logic[edge][0] > 0:
            success = True
        req_items = []
        for req in self.logic[edge][4]:
            i = 0
            while i < req[1]:
                req_items.append(req[0])
                i += 1
        if self.is_sublist(self.items_collected + items, req_items) and (
                self.edge_formless(edge) or self.check_ds_access(self.logic[edge][1], self.logic[edge][3] & form, False,
                                                                 [])):
            success = True
        if success and update_graph and self.logic[edge][0] == 0:
            self.logic[edge][0] = 1
            self.new_connection(self.logic[edge][1], self.logic[edge][2], self.logic[edge][3] & form)
        return success

    # Save a new connection (i.e. exit or edge) for forms to graph, and update DS access
    def new_connection(self, origin, dest, form):
        if dest not in self.graph[origin][10]:
            self.graph[origin][10].append(dest)
        if origin not in self.graph[dest][8]:
            self.graph[dest][8].append(origin)
        if (self.graph[dest][4] & 0x10) and self.consider_ds_node(origin, 0x10, []):
            self.update_ds_access([origin], 0x10, [])  # If dest can reach a DS, origin now can too
        for flag in [0x01, 0x02, 0x04, 0x20]:
            ds_nodes = self.graph[origin][9] if flag == 0x20 else []
            if (self.graph[origin][4] & flag & form) and self.consider_ds_node(dest, flag, ds_nodes):
                self.update_ds_access([dest], flag, ds_nodes)  # dest now reachable from origin's DS nodes
        return True

    # Set up the databases as required by this seed.
    # Future writer: be sure the databases are in the state you expect at the line where you're adding code;
    # for example, exit_logic and artificial grouping items are unused after they're decomposed.
    def initialize(self):
        # Will delete several database objects that aren't needed by this seed
        free_items = []  # Items given for free, whose edges should be kept
        unused_items = []  # Inaccessible items, whose edges should be deleted
        unused_locs = []
        unused_nodes = []
        unused_edges = []
        unused_exits = []

        # Save item shuffle pools in the database
        for item in self.item_pool:
            if self.item_pool[item][6] == 0:
                self.item_pool[item][6] = self.get_pool_id(item=item)
        for loc in self.item_locations:
            if self.item_locations[loc][7] == 0:
                self.item_locations[loc][7] = self.get_pool_id(loc=loc)

        # Save required items
        if 1 in self.dungeons_req:
            self.required_items += [3, 4, 7, 8]
        if 2 in self.dungeons_req:
            self.required_items += [14]
        if 3 in self.dungeons_req:
            self.required_items += [18, 19]
        if 5 in self.dungeons_req:
            self.required_items += [38, 30, 31, 32, 33, 34, 35]
        if 6 in self.dungeons_req:
            self.required_items += [39]
        if self.kara == 1:
            self.required_items += [2, 9, 23]
        elif self.kara == 2:
            self.required_items += [11, 12, 15]
        elif self.kara == 4:
            self.required_items += [26]
        elif self.kara == 5:
            self.required_items += [28, 66]
        
        # Save soft-disallowed items per location (ignored in Chaos logic):
        # No non-W abilities in towns
        non_w_abilities = [item for item in FORM_ITEMS[1] + FORM_ITEMS[2] if self.item_pool[item][6] == 2]
        for loc in self.spawn_locations:
            if loc in self.item_locations and not self.spawn_locations[loc][3]:
                self.item_locations[loc][4].extend(non_w_abilities)
        # Jeweler inventory isn't fun if full of trash or front-loaded with goodies
        for jeweler_loc in [0, 2, 4]:
            self.item_locations[jeweler_loc + random.randint(0, 1)][4].extend([0, 1, 6, 41, 42])
        for jeweler_loc in [0, 1, 2, 3]:
            for item in self.item_pool:
                if self.item_pool[item][7] > 1 + (2 * jeweler_loc) and item not in self.item_locations[jeweler_loc][4]:
                    self.item_locations[jeweler_loc][4].append(item)
        # Restrict bad item placement by difficulty
        if self.difficulty == 0:
            for awful_ds_loc in [31, 111, 146]:   # No abilities in awful Dark Spaces (Castoth, Kress 3, Upper Babel)
                self.item_locations[awful_ds_loc][4].extend([61,62,63,64,65,66])
        if self.difficulty in [0,1]:
            for awful_loc in [136, 147, 740, 741]:   # Killer 6, Jeweler's Mansion
                self.item_locations[awful_loc][4].extend(self.required_items)
            if 1 not in self.statues and self.statue_req != StatueReq.PLAYER_CHOICE.value:
                self.item_locations[32][4].extend(self.required_items)   # Gold Ship restricted if Statue 1 isn't required

        # Clamp item progression penalty
        for item in self.item_pool:
            if self.item_pool[item][7] < -10:
                self.item_pool[item][7] = -10.0
            elif self.item_pool[item][7] > 10:
                self.item_pool[item][7] = 10.0

        # Save implicit FromRegion/ToRegion for coupled exits, and mark exits for randomization.
        for x in self.exits:
            if self.is_exit_coupled(x) and (not self.exits[x][3] or not self.exits[x][4]):
                xprime = self.exits[x][0]
                self.exits[x][3] = self.exits[xprime][4]
                self.exits[x][4] = self.exits[xprime][3]
            if (not self.exits[x][1] and self.get_exit_pool(x) > -1):
                self.exits[x][1] = -1
                self.exits[x][2] = -1

        # Random start location
        if self.start_mode != "South Cape":
            self.start_loc = self.random_start()
            self.info("Start location: " + str(self.item_locations[self.start_loc][6]))
            if self.start_loc == 47:  # Diamond Mine behind fences: fences are free
                self.graph[131][1].append(130)
        if self.start_mode == "South Cape" and not self.entrance_shuffle:
            self.graph[0][1].append(22)  # Starts in school
        else:
            # Connect node 0 to the start; for locs behind orbs, connect to the outer node
            if self.start_loc == 19:
                start_node = 47  # Edward's
            elif self.start_loc == 46:
                start_node = 136  # Mine
            else:
                start_node = self.item_locations[self.start_loc][0]
            self.graph[0][1].append(start_node)
        start_map = self.spawn_locations[self.start_loc][1]
        if start_map in self.maps:
            self.maps[start_map][4] = 1  # Can only start in a dark map if cursed

        # Randomize darkness and add edges to exit_logic if applicable
        if self.darkroom_level not in ["None", "All"]:
            if self.darkroom_level == "Few":
                self.max_darkrooms = 7
            elif self.darkroom_level == "Some":
                self.max_darkrooms = 14
            elif self.darkroom_level == "Many":
                self.max_darkrooms = 21
            if self.darkroom_cursed:
                self.max_darkrooms *= 2
            self.dr_randomize()

        # Pyramid logic is complex; handling it here is "arguably" cleaner than database line items.
        pyramid_portal_nodes = [413, 419, 423, 425, 428, 430, 437, 441, 450]
        pyramid_corridor_exits = [637, 640, 643, 646, 649, 652, 655, 660, 663, 666, 669, 672]
        boss_defeated_items = [503, 532, 531, 533, 534, 522, 523] # in order Castoth->SA
        for node in pyramid_portal_nodes:
            # Pyramid portals are free, except in dungeon shuffle where they require Aura but can be used formlessly
            if not self.dungeon_shuffle:
                self.graph[node][1].append(411)
            else:
                new_edge_id = 1+max(self.logic)
                new_edge = [0, node, 411, 0x0f, [[36, 1]], False]
                self.logic[new_edge_id] = new_edge
        for exit in pyramid_corridor_exits:
            # Pyramid corridors require the "Pyramid in logic" artificial item
            new_edge_id = 1+max(self.exit_logic)
            new_edge = [exit, [[802, 1]], 2, False]
            self.exit_logic[new_edge_id] = new_edge
        for item1 in boss_defeated_items:
            for item2 in boss_defeated_items:
                if item1 != item2:
                    # K6 logical access requires access to any two dungeon bosses.
                    new_edge_id = 1+max(self.logic)
                    new_edge = [0, 0, 803, 0, [[item1, 1], [item2, 1]], False]
                    self.logic[new_edge_id] = new_edge
                    # On Easy difficulty, Pyramid logical access also requires this.
                    if self.difficulty == 0:
                        new_edge_id = 1+max(self.logic)
                        new_edge = [0, 0, 802, 0, [[item1, 1], [item2, 1]], False]
                        self.logic[new_edge_id] = new_edge
            # On Normal difficulty, Pyramid logical access only requires any one boss.
            if self.difficulty == 1:
                new_edge_id = 1+max(self.logic)
                new_edge = [0, 0, 802, 0, [[item1, 1]], False]
                self.logic[new_edge_id] = new_edge
        if self.difficulty >= 2:
            # On difficulty H+, Pyramid is not logic-gated.
            free_items.append(802)
        
        # Convert exits that have logic requirements into graph nodes with logic edges
        coupled_exit_logics = [edge for edge in self.exit_logic if self.exit_logic[edge][3]]
        for edge in coupled_exit_logics:
            this_exit = self.exit_logic[edge][0]
            sister_exit = self.exits[this_exit][0]
            if sister_exit > 0:
                new_edge_id = 1 + max(self.exit_logic)
                new_edge = [sister_exit, self.exit_logic[edge][1][:], self.exit_logic[edge][2], False]
                self.exit_logic[new_edge_id] = new_edge
                self.exit_logic[edge][3] = False
        exits_with_logic = set(self.exit_logic[edge][0] for edge in self.exit_logic)
        for exit in exits_with_logic:
            src_node_id = self.exits[exit][3]
            src_node_type = self.graph[src_node_id][2]
            src_node_info = self.graph[src_node_id][3]
            new_node_id = 1 + max(self.graph)
            new_node = [False, [], src_node_type, src_node_info[:], 0, self.exits[exit][10], [], False, [], [], [], [], [], [], [], []]
            self.graph[new_node_id] = new_node
            sister_exit = self.exits[exit][0]
            exit_edges = [e for e in self.exit_logic if self.exit_logic[e][0] == exit]
            for edge in exit_edges:
                new_edge_id = 1 + max(self.logic)
                if self.exit_logic[edge][2] == 0:  # Logic is for room->exit
                    new_edge = [0, src_node_id, new_node_id, 0, self.exit_logic[edge][1][:], False]
                    self.exits[exit][3] = new_node_id  # Exit is from its own node, sister_exit goes to the room
                    self.graph[new_node_id][1].append(src_node_id)  # Exit->room is free
                elif self.exit_logic[edge][2] == 1:  # Logic is for exit->room
                    new_edge = [0, new_node_id, src_node_id, 0, self.exit_logic[edge][1][:], False]
                    self.graph[src_node_id][1].append(new_node_id)  # Room->exit is free
                    if sister_exit and self.exits[sister_exit][4] == src_node_id:    # Exit is from the room, sister_exit goes to the new exitnode
                        self.exits[sister_exit][4] = new_node_id
                elif self.exit_logic[edge][2] == 2:  # Logic blocks both room->exitnode and exitnode->room
                    new_edge = [0, new_node_id, src_node_id, 0, self.exit_logic[edge][1][:], True]
                    self.exits[exit][3] = new_node_id  # Exit is from its own node
                    if sister_exit and self.exits[sister_exit][4] == src_node_id:    # Sister exit goes to the new exitnode
                        self.exits[sister_exit][4] = new_node_id
                else:  # Something's wrong
                    self.error("exit_logic contains invalid directionality")
                    return False
                self.logic[new_edge_id] = new_edge

        # Convert locations that have logic requirements into graph nodes with logic edges
        for loc in self.item_locations:
            if self.item_locations[loc][9]:
                outer_node_id = self.item_locations[loc][0]
                outer_node_type = self.graph[outer_node_id][2]
                outer_node_info = self.graph[outer_node_id][3]
                loc_name = self.item_locations[loc][6]
                new_node_id = 1 + max(self.graph)
                new_node = [False, [outer_node_id], outer_node_type, outer_node_info[:], 0, loc_name, [], False, [], [],
                            [], [], [], [], [], []]
                new_edge_id = 1 + max(self.logic)
                new_edge = [0, outer_node_id, new_node_id, 0, self.item_locations[loc][9][:], False]
                self.graph[new_node_id] = new_node
                self.logic[new_edge_id] = new_edge
                self.item_locations[loc][0] = new_node_id

        # If no orb rando, assign default locs for all orbs (item ID == loc ID).
        # If additionally starting with flute, give the free orbs as free items.
        # most orbs are free, but programmatically identifying them is complex, so they're hardcoded.
        if self.orb_rando == "None":
            all_orbs = [item for item in self.item_pool if self.item_pool[item][1] == 5]
            free_orbs = [701, 702, 703, 704, 710, 713, 718, 721, 725, 727, 728, 736, 739]  # progression orbs
            free_orbs.extend([item for item in all_orbs if self.item_pool[item][5] == 3])  # nonprog
            for orb in all_orbs:
                loc = orb
                self.unfill_item(loc)
                self.fill_item(orb, loc, False, True)
                if self.flute == "Start" and orb in free_orbs:
                    free_items.append(orb)
                    unused_locs.append(loc)

        # Various gameplay variants
        if self.firebird:
            free_items.append(602)
        else:
            unused_items.append(602)
        if "Z3 Mode" not in self.variant:
            unused_items.append(55)  # Heart pieces don't exist
        if "Open Mode" in self.variant:
            # Replace travel items (Letter, M.Melody, Teapot, Will, Roast)
            free_items.extend([10, 13, 24, 25, 37])
            self.item_pool[6][0] += 4  # Herbs
            self.item_pool[0][0] += 1  # Nothing
        # Some flute shuffle handling.
        if self.flute == "Start":
            # Starting with Flute, so give Flute and Can-Play-Song items
            free_items.append(604)
            free_items.append(611)
        else:
            # Starting without Flute; remove something so there's room for it
            if self.item_pool[0][0] > 0:  # Try removing a Nothing
                self.item_pool[0][0] -= 1
            else:
                self.item_pool[6][0] -= 1  # Or settle for removing an herb
            if self.flute == "Shuffle":
                # Must find the Flute to play songs
                unused_items.append(611)
                song_edges = [e for e in self.logic if
                              e not in unused_edges and any(req[0] == 611 for req in self.logic[e][4])]
                for edge in song_edges:
                    for req in self.logic[edge][4]:
                        if req[0] == 611:
                            req[0] = 604
            if self.flute == "Fluteless":
                # The Flute isn't collectible, but Will can whistle
                unused_items.append(604)
                free_items.append(611)

        # Statue/Endgame logic
        if self.goal == "Red Jewel Hunt":
            unused_edges.extend([406, 407])
            # Mansion is inaccessible, so can't have nontrivial items.
            self.unfill_item(147) # Mansion chest
            unused_locs.append(147)
            if self.item_pool[0][0] > 0:
                self.item_pool[0][0] -= 1
                self.fill_item(0, 147, False, True)
            else:
                self.item_pool[6][0] -= 1
                self.fill_item(6, 147, False, True)
            for orb in [740, 741]:
                unused_locs.append(orb)
                free_items.append(orb)
        else:
            for x in self.statues:
                self.logic[406][4][x][1] = 1
            if self.statue_req == StatueReq.PLAYER_CHOICE.value:
                self.item_pool[106][0] = 6
                unused_items.extend([100, 101, 102, 103, 104, 105])
            else:
                unused_items.append(106)

        # Remove Jeweler edges that require more RJ items than exist, to help the traverser
        if self.gem[6] > self.item_pool[1][0]:
            unused_edges.append(24)
            if self.gem[6] > 2 + self.item_pool[1][0]:
                unused_edges.append(25)
                if self.gem[6] > 3 + self.item_pool[1][0]:
                    unused_edges.append(26)

        # Decompose bidirectional and artificial-item edges to unidirectional with real items;
        # the former are easier to maintain, the latter allow simpler code
        bidirectional_edges = [edge for edge in self.logic if self.logic[edge][5] and edge not in unused_edges]
        for edge in bidirectional_edges:
            self.logic[edge][5] = False
            new_edge_id = 1 + max(self.logic)
            self.logic[new_edge_id] = [self.logic[edge][0], self.logic[edge][2], self.logic[edge][1],
                                       self.logic[edge][3], self.logic[edge][4][:], False]
        any_will_ability_edges = [edge for edge in self.logic if
                                  any(req[0] == 608 for req in self.logic[edge][4]) and edge not in unused_edges]
        unused_items.append(608)
        unused_edges.extend(any_will_ability_edges)
        for edge in any_will_ability_edges:
            self.logic[edge][4].remove([608, 1])
            for will_ability in [61, 62, 63]:
                new_edge_id = 1 + max(self.logic)
                self.logic[new_edge_id] = [self.logic[edge][0], self.logic[edge][1], self.logic[edge][2],
                                           self.logic[edge][3], self.logic[edge][4][:] + [[will_ability, 1]],
                                           self.logic[edge][5]]
        any_ranged_ability_edges = [edge for edge in self.logic if
                                    any(req[0] == 610 for req in self.logic[edge][4]) and edge not in unused_edges]
        unused_items.append(610)
        unused_edges.extend(any_ranged_ability_edges)
        for edge in any_ranged_ability_edges:
            self.logic[edge][4].remove([610, 1])
            for ranged_ability in [64, 67]:  # Friar-0, Firebird
                new_edge_id = 1 + max(self.logic)
                self.logic[new_edge_id] = [self.logic[edge][0], self.logic[edge][1], self.logic[edge][2],
                                           self.logic[edge][3], self.logic[edge][4][:] + [[ranged_ability, 1]],
                                           self.logic[edge][5]]
                if ranged_ability == 67:
                    self.logic[new_edge_id][4].append([602, 1])
        if self.flute == "Start":
            # If we start with flute, we have Any-Attack and Telekinesis
            free_items.append(609)
            free_items.append(612)
        else:
            any_attack_edges = [edge for edge in self.logic if
                                any(req[0] == 609 for req in self.logic[edge][4]) and edge not in unused_edges]
            unused_items.append(609)
            unused_edges.extend(any_attack_edges)
            for edge in any_attack_edges:
                self.logic[edge][4].remove([609, 1])
                new_edge_id = 1 + max(self.logic)
                self.logic[new_edge_id] = [self.logic[edge][0], self.logic[edge][1], self.logic[edge][2], 0x06,
                                           self.logic[edge][4][:], self.logic[edge][5]]  # F/S always have an attack
                for attack_item in [61, 62, 63, 64, 65, 67, 604]:
                    new_edge_id = 1 + max(self.logic)
                    self.logic[new_edge_id] = [self.logic[edge][0], self.logic[edge][1], self.logic[edge][2], 0,
                                               self.logic[edge][4][:] + [[attack_item, 1]], self.logic[edge][5]]
                    if attack_item == 67:
                        self.logic[new_edge_id][4].append([602, 1])  # Firebird is an attack only if Firebird is enabled
            if self.flute == "Fluteless":
                # Telekinesis is free in Fluteless
                free_items.append(612)
            else:
                # Replace telekinesis edges with F/S and Flute edges
                telekinesis_edges = [edge for edge in self.logic if
                                     any(req[0] == 612 for req in self.logic[edge][4]) and edge not in unused_edges]
                unused_items.append(612)
                unused_edges.extend(telekinesis_edges)
                for edge in telekinesis_edges:
                    self.logic[edge][4].remove([612, 1])
                    new_edge_id = 1 + max(self.logic)
                    self.logic[new_edge_id] = [self.logic[edge][0], self.logic[edge][1], self.logic[edge][2], 0x06,
                                               self.logic[edge][4][:], self.logic[edge][5]]
                    new_edge_id = 1 + max(self.logic)
                    self.logic[new_edge_id] = [self.logic[edge][0], self.logic[edge][1], self.logic[edge][2], 0,
                                               self.logic[edge][4][:] + [[604, 1]], self.logic[edge][5]]

        # Dungeon Shuffle.
        # Clean up unused nodes and artificial items
        if not self.dungeon_shuffle:  # if self.dungeon_shuffle == "None" or self.dungeon_shuffle == "Basic":
            free_items.append(525)  # Pyramid portals open
            unused_locs.append(525)  # Loc is unused as item is free
            unused_nodes.append(525)  # Node is unused as item is free
            if True:  # self.dungeon_shuffle == "None":
                unused_items.append(800)
                free_items.append(801)
        if self.dungeon_shuffle and self.coupled_exits:  # == "Chaos":
            # Reduce walking times by removing some empty corridors; stabilize dungeon generation by removing lower Mu corridors.
            # Inca U-turn + statue "puzzle"; Mine elevator; Angl empty water room;
            # Wat hall before + road to main hall, + corridor before spirit.
            useless_exits = [118, 119, 137, 138, 225, 236, 237, 238, 239, 240, 398, 407, 583, 584, 585, 586, 597, 598,
                             359, 360, 365, 366]
            useless_nodes = list(set([self.exits[x][3] for x in useless_exits]))
            useless_edges = []
            useless_node_count = 0
            while useless_node_count < len(useless_nodes):
                useless_node_count = len(useless_nodes)
                for i in range(len(useless_nodes)):
                    n = useless_nodes[i]
                    useless_nodes.extend(self.graph[n][1])
                    for o in self.graph[n][1]:
                        useless_nodes.extend([p for p in self.graph if o in self.graph[p][1]])
                    here_edges = [e for e in self.logic if self.logic[e][1] == n or self.logic[e][2] == n]
                    useless_nodes.extend(
                        [self.logic[e][1] for e in here_edges] + [self.logic[e][2] for e in here_edges])
                    unused_edges.extend(here_edges)
                useless_nodes = list(set(useless_nodes))
            unused_nodes.extend(useless_nodes)
            unused_exits.extend(useless_exits)

        # Save explicit form requirements in the logic database
        for edge in self.logic:
            if self.logic[edge][3] == 0 and self.logic[edge][4]:  # Edges with no reqs will be cleaned up later
                reqs = self.logic[edge][4]
                if not any(req[0] in FORM_ITEMS[f] for f in [0, 1, 2] for req in reqs):
                    self.logic[edge][3] = 0x27
                else:
                    self.logic[edge][3] |= (0x01 * any(req[0] in FORM_ITEMS[0] for req in reqs))
                    self.logic[edge][3] |= (0x02 * any(req[0] in FORM_ITEMS[1] for req in reqs))
                    self.logic[edge][3] |= (0x04 * any(req[0] in FORM_ITEMS[2] for req in reqs))

        # Clean up the objects so designated based on seed settings
        self.delete_objects(items=unused_items, locs=unused_locs, nodes=unused_nodes, edges=unused_edges,
                            exits=unused_exits, with_close=True)
        self.delete_objects(items=free_items, with_close=False)

        # Clean up edges that now require neither items nor a specific form, or that go nowhere
        free_edges = [edge for edge in self.logic if self.edge_formless(edge) and not self.logic[edge][4]]
        free_edges.extend([edge for edge in self.logic if self.logic[edge][1] == self.logic[edge][2]])
        for edge in free_edges:
            here_node = self.logic[edge][1]
            other_node = self.logic[edge][2]
            self.graph[here_node][1].append(other_node)
        self.delete_objects(edges=free_edges, with_close=True)

        # Incorporate item locations and logic edges into world graph
        for x in self.item_locations:
            self.graph[self.item_locations[x][0]][11].append(x)
        for y in self.logic:
            if self.logic[y][0] != -1:
                self.graph[self.logic[y][1]][12].append(y)
                self.graph[self.logic[y][2]][13].append(y)

        # Boss Shuffle: boss_order[n] is the boss of dungeon n, 0<=n<=6, 1<=boss<=7
        if "Boss Shuffle" in self.variant:
            boss_door_exits = [1, 4, 7, 10, 13, 16, 19]
            boss_defeat_exits = [3, 6, 9, 12, 15, 18, 21]
            self.verbose("Boss order: " + str(self.boss_order))
            for dungeon in range(7):
                this_dungeon_boss = self.boss_order[dungeon]
                normal_boss_exit = boss_door_exits[dungeon]
                new_boss_exit = boss_door_exits[this_dungeon_boss - 1]
                self.link_exits(normal_boss_exit, new_boss_exit)
                normal_defeat_exit = boss_defeat_exits[dungeon]
                new_defeat_exit = boss_defeat_exits[this_dungeon_boss - 1]
                self.link_exits(new_defeat_exit, normal_defeat_exit)
                # In RJH, don't path through the inaccessible Mansion boss
                if self.goal == "Red Jewel Hunt" and dungeon == 6:
                    self.exits[new_defeat_exit][4] = self.exits[new_defeat_exit][3]

        # Cache the number of item pools, and create empty loc lists for them
        self.item_pool_count = 1 + self.get_max_pool_id()
        self.open_locations = [[] for _ in range(self.item_pool_count)]

        self.reset_progress(True)  # Initialize graph with no items or logic
        self.update_graph(True, True, True)  # Build basic graph connections from any unrandomized elements

        return True

    # Delete or hide sets of objects and linked objects. If with_close, an edge is deleted if any
    # required item is deleted; otherwise the item is just removed as a requirement.
    # Deleted objects are retained in deleted_* dicts to maintain their assembly labels and referential integrity.
    # For that reason, deleted items and locs aren't unfilled.
    # Exits remain in self.exits because, when shuffling, other exits still need to act-like the deleted exit.
    def delete_objects(self, items=[], locs=[], nodes=[], edges=[], exits=[], with_close=True):
        del_items = [x for x in items if x in self.item_pool]
        del_locs = [x for x in locs if x in self.item_locations]
        del_nodes = [x for x in nodes if x in self.graph and x > 0]
        del_edges = [x for x in edges if x in self.logic]
        del_exits = [x for x in exits if x in self.exits and x not in self.deleted_exits]
        for item in set(del_items):
            self.deleted_item_pool[item] = self.item_pool[item]
            for node in [n for n in self.graph if item in self.graph[n][6]]:
                self.graph[node][6].remove(item)
            affected_edges = [e for e in self.logic if any(item == req[0] for req in self.logic[e][4])]
            for edge in affected_edges:
                if with_close:
                    del_edges.append(edge)
                else:
                    req = next(r for r in self.logic[edge][4] if r[0] == item)
                    self.logic[edge][4].remove(req)
            del self.item_pool[item]
        for node in set(del_nodes):
            self.deleted_graph[node] = self.graph[node]
            affected_locs = [loc for loc in self.item_locations if self.item_locations[loc][0] == node]
            affected_nodes = [n for n in self.graph if
                              node in self.graph[n][1] + self.graph[n][8] + self.graph[n][9] + self.graph[n][10]]
            affected_edges = [e for e in self.logic if node == self.logic[e][1] or node == self.logic[e][2]]
            affected_exits = [x for x in self.exits if self.exits[x][3] == node or self.exits[x][4] == node]
            del_locs.extend(affected_locs)
            del_edges.extend(affected_edges)
            for other_node, subidx in itertools.product(affected_nodes, [1, 8, 9, 10]):
                if node in self.graph[other_node][subidx]:
                    self.graph[other_node][subidx].remove(node)
            for exit in affected_exits:
                if self.exits[exit][3] == node:
                    self.exits[exit][3] = -1  # Exit source becomes "inaccessible"
                if self.exits[exit][4] == node:
                    self.exits[exit][4] = -2  # Exit dest becomes "deleted"
            del self.graph[node]
        for loc in set(del_locs):
            self.deleted_item_locations[loc] = self.item_locations[loc]
            affected_nodes = [n for n in self.graph if loc in self.graph[n][11]]
            for node in affected_nodes:
                self.graph[node][11].remove(loc)
            del self.item_locations[loc]
        for edge in set(del_edges):
            self.deleted_logic[edge] = self.logic[edge]
            affected_nodes = [n for n in self.graph if edge in self.graph[n][12] + self.graph[n][13]]
            for node in affected_nodes:
                for subidx in [12, 13]:
                    if edge in self.graph[node][subidx]:
                        self.graph[node][subidx].remove(edge)
            del self.logic[edge]
        for exit in set(del_exits):
            if self.exits[exit][1] < 0 and self.exits[exit][0] > 0:
                self.link_exits(exit, self.exits[exit][0], False, False)
            self.deleted_exits[exit] = self.exits[exit]
            affected_nodes = [n for n in self.graph if exit in self.graph[n][14] + self.graph[n][15]]
            for node, subidx in itertools.product(affected_nodes, [14, 15]):
                if exit in self.graph[node][subidx]:
                    self.graph[node][subidx].remove(exit)

    # Simulate inventory
    def get_inventory(self, start_items=[], item_destinations=[], new_nodes=[]):
        if not start_items:
            start_items = self.items_collected[:]
        if not item_destinations:
            item_destinations = self.item_destinations[:]
        inventory_temp = []
        for item in start_items:
            if self.item_pool[item][4]:
                inventory_temp.append(item)
        inventory = []
        while inventory_temp:
            item = inventory_temp.pop(0)
            if item in item_destinations:
                item_destinations.remove(item)
            else:
                inventory.append(item)
        return inventory

    # Takes a random seed and builds out a randomized world
    def randomize(self, seed_adj=0, printlevel=-1, break_on_error=False, break_on_init=False):
        self.printlevel = printlevel
        self.break_on_error = break_on_error

        random.seed(self.seed + seed_adj)  # 3229535
        if self.race_mode:
            for i in range(random.randint(100, 1000)):
                _ = random.randint(0, 10000)

        if break_on_init:
            breakpoint()
        if not self.initialize():
            self.error("Could not initialize world")
            return False
        self.info("Initialization complete")
        for item in self.item_pool:
            self.base_item_counts[item] = self.item_pool[item][0]

        # Overworld shuffle
        if "Overworld Shuffle" in self.variant:
            if not self.shuffle_overworld():
                self.error("Overworld shuffle failed")
                return False

        # Shuffle exits
        if self.entrance_shuffle:
            if not self.shuffle_exits():
                self.error("Entrance rando failed")
                return False

        self.reset_progress(True)  # Forget items and logic used for ER/DS skeleton construction
        self.update_graph(True, True, True)  # Rebuild graph connections with exits

        # Initialize and shuffle location list
        item_locations = self.list_item_locations(shuffled_only=True)
        random.shuffle(item_locations)

        # Populate various pseudo-item pools
        self.fill_statues()
        self.map_rewards()

        # Populate Dark Spaces; all non-DS items are granted so traversal can go to all DS-requiring edges
        self.reset_progress(True)
        self.items_collected = self.list_typed_items(types=[1], shuffled_only=False, incl_placed=True)
        if self.orb_rando != "None":
            self.items_collected.extend(self.list_typed_items(types=[5], shuffled_only=False, incl_placed=True))
        self.update_graph(True, True, True)
        ds_items = self.list_typed_items(types=[2], shuffled_only=True, incl_placed=False)
        random.shuffle(ds_items)
        self.info("Populating Dark Spaces...")
        cycle = 0
        while True:
            cycle += 1
            if cycle >= MAX_CYCLES:
                self.error("Couldn't populate DS items for an unknown reason")
                return False
            if not ds_items:
                # All remaining unoccupied dungeon DSes are for transform
                for loc in self.spawn_locations:
                    if self.spawn_locations[loc][3] and loc in self.item_locations and self.item_locations[loc][
                        1] == 2 and not self.item_locations[loc][3]:
                        self.item_locations[loc][2] = True
                self.verbose("All remaining Dark Spaces are locked for transform")
                self.update_graph(True, True, False)
                if self.logic_mode != "Completable":
                    break  # Good enough: all DSes are populated and formful access isn't mandatory
            traverse_result = self.traverse()
            new_nodes = traverse_result[0]
            # A node needs a txform DS if it has an open formful edge, isn't accessible by that form, and the edge goes to an unreached area
            f_missing_nodes = {self.logic[e][1] for e in self.open_edges if not self.edge_formless(e) and not (
                    self.logic[e][3] & self.graph[self.logic[e][1]][4]) and not self.is_accessible(
                self.logic[e][2])}
            if not f_missing_nodes and not ds_items:
                break  # Success: no DS items left to place and no open formful edges to new areas
            made_progress = False
            if f_missing_nodes:
                # Lock txform DSes to cover nodes that need a form and aren't known to be accessible by that form
                f_nodes_under_ds_node = {}
                for node in f_missing_nodes:
                    for ds_node in self.graph[node][9]:
                        if not self.graph[ds_node][0]:
                            continue
                        ds_loc = next(loc for loc in self.graph[ds_node][11] if self.item_locations[loc][1] == 2)
                        if self.graph[ds_node][0] and not self.item_locations[ds_loc][2]:
                            if ds_node not in f_nodes_under_ds_node:
                                f_nodes_under_ds_node[ds_node] = set()
                            f_nodes_under_ds_node[ds_node].add(node)
                while f_missing_nodes and f_nodes_under_ds_node:
                    # Lock the DS that covers the most remaining f nodes, breaking ties randomly
                    lock_node = max(f_nodes_under_ds_node, key=lambda ds_node: len(
                        f_missing_nodes.intersection(f_nodes_under_ds_node[ds_node])) + random.random())
                    lock_loc = next(loc for loc in self.item_locations if
                                    self.item_locations[loc][0] == lock_node and self.item_locations[loc][1] == 2)
                    self.item_locations[lock_loc][
                        2] = True  # Mark the DS as occupied, remove it from the pool, and clear its contents if any
                    if self.item_locations[lock_loc][3]:
                        self.unfill_item(lock_loc)
                    self.item_locations[lock_loc][7] = 0
                    self.info(" Locked for transform: " + str(self.item_locations[lock_loc][6]))
                    made_progress = True
                    f_missing_nodes = f_missing_nodes.difference(f_nodes_under_ds_node[lock_node])
                    for covered_node in f_nodes_under_ds_node[lock_node]:
                        for ds_node in f_nodes_under_ds_node:
                            if ds_node != lock_node and covered_node in f_nodes_under_ds_node[ds_node]:
                                f_nodes_under_ds_node[ds_node].remove(covered_node)
                    del f_nodes_under_ds_node[lock_node]
                    while any(len(f_nodes_under_ds_node[ds_node]) == 0 for ds_node in f_nodes_under_ds_node):
                        del f_nodes_under_ds_node[next(
                            ds_node for ds_node in f_nodes_under_ds_node if len(f_nodes_under_ds_node[ds_node]) == 0)]
                if len(f_missing_nodes) > 0 and not made_progress and not ds_items:
                    # Can't expand formful access, and there are no more items to grant progress, so we're stuck
                    for n in f_missing_nodes:
                        self.warn("No formless access from or formful access to " + str(n) + " " + self.graph[n][5])
                    if self.logic_mode == "Completable":
                        self.error("World is unsolvable: missing form access")
                        return False
                # Reinitialize Dark Space access since more may now be for transform
                self.update_graph(True, True, False)
            if ds_items:
                # Now no accessible nodes are missing a form due to DS access, so we can safely place a DS item
                progression_result = self.progression_list(ignore_inv=True, penalty_threshold=(6 - len(ds_items)))
                if not progression_result[0]:  # try again without the penalty
                    progression_result = self.progression_list(ignore_inv=True)
                progression_list = [itemset for itemset in progression_result[0] if itemset[0] in ds_items]
                if progression_list:
                    # Monte Carlo style
                    key = random.uniform(0, 100)
                    progression_mc = self.monte_carlo(progression_list)
                    idx = 0
                    for x in progression_mc:
                        if key <= x[0] and not idx:
                            idx = x[1]
                    items = progression_list.pop(idx)
                    if self.forward_fill(items, item_locations, False, self.logic_mode == "Chaos"):
                        self.info(" Placed " + self.item_pool[items[0]][3] + " for progression")
                        made_progress = True
                        for item in items:
                            ds_items.remove(item)
                elif len(new_nodes) == 1:  # (the start node always counts as new)
                    # The graph is maxed out and the other DS items aren't progression, so place them randomly
                    if self.forward_fill(ds_items, item_locations, False, self.logic_mode == "Chaos"):
                        self.info(" Placed remaining DS items")
                        made_progress = True
                        ds_items = []
            if not made_progress:
                if len(f_missing_nodes) > 0 and len(ds_items) > 0:
                    self.error("World is unsolvable: can't lock a txform DS nor place a DS item")
                elif len(f_missing_nodes) > 0 and len(ds_items) == 0:
                    self.error("World is unsolvable: can't lock any more DSes")
                elif len(f_missing_nodes) == 0 and len(ds_items) > 0:
                    self.error("World is unsolvable: can't place remaining DS items")
                else:
                    self.error("Dark Spaces were populated without logging progress")
                return False
        # Randomly place non-progression items in the open graph
        self.info("Placing junk...")
        non_prog_items = self.list_typed_items(types=[], progress_type=3, shuffled_only=True)
        for item in non_prog_items:
            if item in self.items_collected:
                self.items_collected.remove(item)
        self.forward_fill(non_prog_items, item_locations, False, self.logic_mode == "Chaos")
        # Forget collected items and edges; rebuild the graph with DSes set, ready to place items
        self.info("Beginning item placement...")
        self.reset_progress(True)
        self.update_graph(True, True, False)  # no need to recalculate exits again
        high_penalty_items = {item for item in self.item_pool if self.item_pool[item][7] > 1}
        for loc in self.item_locations:
            self.item_locations[loc][8] = MAX_CYCLES  # Initialize discovered-on-cycle value
        done = False
        goal = False
        cycle = 0
        while not done:
            cycle += 1
            self.info(" Cycle " + str(cycle))
            if cycle > MAX_CYCLES:
                self.error("Max cycles exceeded in item placement")
                return False
            self.traverse()
            # Good items resist being placed early; if starting in a town with lots of checks available, very good items can't be placed early at all
            discovered_locs = [loc for loc in self.item_locations if self.graph[self.item_locations[loc][0]][0] and self.item_locations[loc][8] > cycle]
            for loc in discovered_locs:
                self.item_locations[loc][8] = cycle
                for item in high_penalty_items:
                    if (item not in self.item_locations[loc][4]) and (cycle < (self.item_pool[item][7] * 1.5 / PROGRESS_ADJ[self.difficulty])) and (self.spawn_locations[self.start_loc][0] == "Safe"):
                        self.item_locations[loc][4].append(item)
            if len(self.get_inventory()) > MAX_INVENTORY:
                goal = False
                self.warn("Inventory capacity exceeded")
            else:
                goal = self.is_accessible(492)

            progression_result = [[], [], []]
            trial_penalty = cycle / 4
            while not progression_result[0] and trial_penalty <= 8 * cycle:
                # The penalty threshold is lightened until progression is found
                progression_result = self.progression_list(penalty_threshold=trial_penalty)
                trial_penalty *= 2
            self.verbose("Progression options: {")
            self.verbose(" " + str(progression_result[0]))  # Available
            self.verbose(" " + str(progression_result[1]))  # Not enough locs
            self.verbose(" " + str(progression_result[2]))  # Not enough inv space
            self.verbose("}")
            progression_list = progression_result[0]
            is_progression = (progression_result != [[], [], []])
            done = goal and (self.logic_mode != "Completable" or not is_progression)

            if not done:
                if not is_progression:
                    self.error("World is unsolvable: can't progress further")
                    return False

                progress = False
                key = random.uniform(0, 100)
                while not progress and progression_list:
                    progression_mc = self.monte_carlo(progression_list)
                    idx = 0
                    for x in progression_mc:
                        if key <= x[0] and not idx:
                            idx = x[1]
                    items = progression_list.pop(idx)
                    if self.forward_fill(items, item_locations, False, self.logic_mode == "Chaos", True):
                        progress = True
                        self.info("  Placed " + str(len(items)) + " items successfully")
                if not progress:
                    self.info("Removing some junk to make room...")
                    if not self.make_room(progression_result):
                        self.error("World is unsolvable: can't place progression items")
                        return False

        self.info("Placing leftover items...")
        junk_items = self.list_typed_items(types=[], shuffled_only=True)
        self.random_fill(junk_items, item_locations, False)

        self.info("Verifying completion...")

        self.reset_progress(True)
        self.update_graph()
        self.traverse([])  # Fresh traverse with no nodes queued to visit

        if self.logic_mode == "Completable":
            completed = all(self.graph[node][0] for node in self.graph if node not in self.optional_nodes)
        else:
            completed = self.graph[492][0]
        if not completed:
            # self.print_graph()
            unreachable = [node for node in self.graph if not self.graph[node][0] and node not in self.optional_nodes]
            for node in unreachable:
                self.warn("Can't reach node " + str(node) + " " + str(self.graph[node]))
            self.error("Seed failed, trying again...")
            return False

        self.info("Writing hints...")
        placement_log = self.placement_log[:]
        random.shuffle(placement_log)
        self.in_game_spoilers(placement_log)

        self.info("Randomization complete")

        return True

    def print_graph(self):
        self.info("Open edges: " + str(self.open_edges))
        self.info("Open locations: " + str(self.open_locations))
        for node in self.graph:
            self.info(str(node) + " " + str(self.graph[node]))

    # Prepares dataset to give in-game spoilers
    def in_game_spoilers(self, placement_log=[]):
        for x in placement_log:
            item = x[0]
            location = x[1]
            if location not in self.free_locations and location in self.area_short_name:
                if item in self.required_items or item in self.good_items or location in self.trolly_locations:
                    spoiler_str = self.area_short_name[location] + " has ]"  # ']' is a newline
                    if len(self.item_pool[item][3]) >= 26:
                        spoiler_str += self.item_pool[item][3].replace(' ', '_', 2).replace(' ', ']', 1)
                    else:
                        spoiler_str += self.item_pool[item][3]
                    # No in-game spoilers in Expert mode
                    if self.difficulty >= 3:
                        spoiler_str = "nice try dodongo!"
                    self.spoilers.append(spoiler_str)
                    # print item, location

    # Prints item and ability locations
    def generate_spoiler(self, version=""):
        if self.kara == 1:
            kara_txt = "Edward's Castle"
        elif self.kara == 2:
            kara_txt = "Diamond Mine"
        elif self.kara == 3:
            kara_txt = "Angel Dungeon"
        elif self.kara == 4:
            kara_txt = "Mt. Kress"
        elif self.kara == 5:
            kara_txt = "Ankor Wat"

        if self.difficulty == 0:
            difficulty_txt = "Easy"
        elif self.difficulty == 1:
            difficulty_txt = "Normal"
        elif self.difficulty == 2:
            difficulty_txt = "Hard"
        elif self.difficulty == 3:
            difficulty_txt = "Extreme"

        spoiler = dict()
        spoiler["version"] = version
        spoiler["seed"] = str(self.seed)
        spoiler["date"] = str(datetime.utcfromtimestamp(time.time()))
        spoiler["goal"] = str(self.goal)
        spoiler["town_shuffle"] = str(self.town_shuffle)
        spoiler["dungeon_shuffle"] = str(self.dungeon_shuffle)
        spoiler["start_location"] = self.item_locations[self.start_loc][6].strip()
        spoiler["logic"] = str(self.logic_mode)
        spoiler["difficulty"] = str(difficulty_txt)
        if self.statue_req == StatueReq.PLAYER_CHOICE.value:
            spoiler["statues_required"] = self.statues_required
        else:
            spoiler["statues_required"] = self.statues
        spoiler["boss_order"] = self.boss_order
        spoiler["kara_location"] = kara_txt
        spoiler["jeweler_amounts"] = self.gem
        spoiler["inca_tiles"] = self.incatile
        spoiler["hieroglyph_order"] = self.hieroglyphs

        items = []
        for x in self.item_locations:
            loc_type = self.item_locations[x][1]
            if loc_type in [1, 2, 3] or (self.orb_rando != "None" and loc_type == 5):
                item = self.item_locations[x][3]
                location_name = self.item_locations[x][6].strip()
                item_name = self.item_pool[item][3]
                items.append({"location": location_name, "name": item_name})
        spoiler["items"] = items

        if "Overworld Shuffle" in self.variant:
            overworld_links = []
            for continent_id, continent_data in OVERWORLD_MENUS.items():
                continent_name = continent_data[5]
                region_name = OVERWORLD_MENUS[continent_data[0]][6]
                region_name = region_name.replace('_', '')
                overworld_links.append({"region": region_name, "continent": continent_name})
            spoiler["overworld_entrances"] = overworld_links

        if self.entrance_shuffle:
            exit_links = []
            for exit in self.exits:
                exit_name = self.exits[exit][10]
                linked_exit = self.exits[exit][1]
                if linked_exit:  # i.e. this acts like linked_exit, going to the area normally on the other side of linked_exit
                    coupled_linked_exit = self.exits[linked_exit][0]
                    if coupled_linked_exit:  # in this case the exit leads to where the acted-like exit's coupled exit is
                        target_name = "Near " + self.exits[coupled_linked_exit][10]
                    else:  # the acted-like exit is one-way, so derive a destination name from the exit name
                        target_name = "Target of " + self.exits[linked_exit][10]
                    exit_links.append({"transition": exit_name, "destination": target_name})
            spoiler["exit_links"] = exit_links

        self.spoiler = spoiler

    # Prints item and ability locations
    def print_spoiler(self):
        if self.kara == 1:
            kara_txt = "Edward's Castle"
        elif self.kara == 2:
            kara_txt = "Diamond Mine"
        elif self.kara == 3:
            kara_txt = "Angel Dungeon"
        elif self.kara == 4:
            kara_txt = "Mt. Kress"
        elif self.kara == 5:
            kara_txt = "Ankor Wat"

        self.info("")
        self.info("Seed                                   >  " + str(self.seed))
        self.info("Statues Required                       >  " + str(self.statues))
        self.info("Kara Location                          >  " + str(kara_txt))
        self.info("Jeweler Reward Amounts                 >  " + str(self.gem))
        self.info("Inca Tile (column, row)                >  " + str(self.incatile))
        self.info("Hieroglyph Order                       >  " + str(self.hieroglyphs))
        self.info("")

        for x in self.item_locations:
            item = self.item_locations[x][3]
            location_name = self.item_locations[x][6]
            item_name = self.item_pool[item][3]
            self.info(str(location_name) + "  >  " + str(item_name))

    # Generate assembly define dict based on World state
    def populate_asar_defines(self):
        # Room-clearing rewards
        for i in range(0x100):
            self.asar_defines["RoomClearReward" + format(i, "02X")] = 0
        idx_tier2 = 1
        idx_tier3 = 1
        idx_tier4 = 1
        for i in range(1, 7):
            self.asar_defines["RemovedRoomRewardExpertFlag" + str(i)] = 0
            self.asar_defines["RemovedRoomRewardAdvancedFlag" + str(i)] = 0
            self.asar_defines["RemovedRoomRewardIntermediateFlag" + str(i)] = 0
        for map in self.maps:
            reward_tier = self.maps[map][2][1]
            if reward_tier > 0:
                reward = self.maps[map][2][0]
                self.asar_defines["RoomClearReward" + format(map, "02X")] = reward
                # Populate player level logic
                if reward_tier == 4:
                    self.asar_defines["RemovedRoomRewardIntermediateFlag" + str(idx_tier2)] = 0x300 + map
                    idx_tier2 += 1
                elif reward_tier == 3:
                    self.asar_defines["RemovedRoomRewardAdvancedFlag" + str(idx_tier3)] = 0x300 + map
                    idx_tier3 += 1
                elif reward_tier == 2:
                    self.asar_defines["RemovedRoomRewardExpertFlag" + str(idx_tier4)] = 0x300 + map
                    idx_tier4 += 1

        # Item placement
        ds_loc_idx = 1
        item_db = {}
        loc_db = {}
        for loc in self.item_locations:
            loc_db[loc] = self.item_locations[loc]
        for loc in self.deleted_item_locations:  # Currently used for deleted (free) orb locs
            loc_db[loc] = self.deleted_item_locations[loc]
        for item in self.item_pool:
            item_db[item] = self.item_pool[item]
        for item in self.deleted_item_pool:
            item_db[item] = self.deleted_item_pool[item]
        for x in loc_db:
            loc_type = loc_db[x][1]
            loc_label = loc_db[x][5]
            # Normal-item and orb locs always have an item, even if empty
            if loc_type == 1 or loc_type == 5:
                item = loc_db[x][3]
                item_id = item_db[item][2]
                self.asar_defines[loc_label] = item_id
            # Only six DS locs have items
            elif loc_type == 2:
                item = loc_db[x][3]
                item_id = item_db[item][2]
                map = self.spawn_locations[x][1]
                if item_id:
                    self.asar_defines["DarkSpaceItem" + str(ds_loc_idx) + "Item"] = item_id
                    self.asar_defines["DarkSpaceItem" + str(ds_loc_idx) + "Map"] = map
                    ds_loc_idx += 1

        # Write in-game spoilers
        i = 0
        for label in SPOILER_LABELS:
            if i < len(self.spoilers):
                self.asar_defines[SPOILER_LABELS[label]] = self.spoilers[i]
                i += 1

        # Enemizer; labels are generated in the routine
        if self.enemizer != "None":
            self.enemize()

        # Start location handling for random start or entrance rando
        self.asar_defines["StartAtWarpLocation"] = 0
        self.asar_defines["StartDsIndex"] = self.spawn_locations[-1][2]
        self.asar_defines["StartLocationName"] = "South Cape"
        self.asar_defines["StartLocationId"] = 10
        if self.start_mode != "South Cape" or self.town_shuffle:
            self.asar_defines["StartAtWarpLocation"] = 1
            self.asar_defines["StartDsIndex"] = self.spawn_locations[self.start_loc][2]
            self.asar_defines["StartLocationName"] = self.area_short_name[self.start_loc]
            self.asar_defines["StartLocationId"] = self.start_loc

        # Overworld
        for entry in OVERWORLD_MENUS:
            new_entry = entry
            if OVERWORLD_MENUS[entry][0] > 0:
                new_entry = OVERWORLD_MENUS[entry][0]
            old_label = OVERWORLD_MENUS[entry][4]
            new_label = OVERWORLD_MENUS[new_entry][4]
            self.asar_defines["OverworldShuffle" + old_label + "Label"] = new_label
            self.asar_defines["OverworldShuffle" + old_label + "Text"] = OVERWORLD_MENUS[new_entry][6]
            self.asar_defines["OverworldShuffle" + new_label + "MenuId"] = OVERWORLD_MENUS[entry][1]

        # Entrances
        for exit in self.exits:
            new_exit = self.exits[exit][1]
            if new_exit > 0:
                old_exit_label = self.exits[exit][5]
                new_exit_string_label = self.exits[new_exit][5]
                self.asar_defines[old_exit_label] = "!Default" + new_exit_string_label

        # Dark rooms
        if self.darkroom_level != "None":
            self.asar_defines["SettingDarkRoomsLevel"] = {"None": 0, "Few": 1, "Some": 2, "Many": 3, "All": 4}[
                self.darkroom_level]
            if len(self.all_darkrooms) > 0:
                darkroom_str = ""
                for room in self.all_darkrooms:
                    darkroom_str += str(room) + ","
                    self.asar_defines["IsMap" + format(room, "02X") + "Dark"] = 1
                darkroom_str += "$ff"
                self.asar_defines["DarkMapList"] = darkroom_str

        # print "ROM successfully created"

    # Pick random start location
    def random_start(self):
        if self.start_mode == "Safe":
            locations = [loc for loc in self.spawn_locations if self.spawn_locations[loc][0] == "Safe"]
        elif self.start_mode == "Unsafe":
            locations = [loc for loc in self.spawn_locations if
                         self.spawn_locations[loc][0] == "Safe" or self.spawn_locations[loc][0] == "Unsafe"]
        else:  # "Forced Unsafe"
            locations = [loc for loc in self.spawn_locations if
                         self.spawn_locations[loc][0] == "Unsafe" or self.spawn_locations[loc][0] == "Forced Unsafe"]
        return locations[random.randint(0, len(locations) - 1)]

    # Dark rooms.
    def dr_randomize(self):
        if self.darkroom_cursed:
            max_cluster_size = 5
        else:
            max_cluster_size = 3
        darkness_clusters = []
        curr_cluster_idx = -1
        while len(self.all_darkrooms) < self.max_darkrooms:
            # If exactly 1 more room is needed, try growing an existing cluster
            if len(self.all_darkrooms) == self.max_darkrooms - 1:
                this_cluster_idx = 0
                while this_cluster_idx < len(darkness_clusters) - 1:
                    candidate_cluster = darkness_clusters[this_cluster_idx]
                    if len(candidate_cluster) < max_cluster_size:
                        if self.dr_spread_once(candidate_cluster):
                            break  # It grew
                    this_cluster_idx += 1
            # If that didn't work or doesn't apply, add a new cluster
            if len(self.all_darkrooms) < self.max_darkrooms:
                darkness_sources = [m for m in self.maps if self.maps[m][4] == 3 and m not in self.all_darkrooms]
                random.shuffle(darkness_sources)
                new_cluster = []
                new_source = darkness_sources.pop(0)
                if any(abs(m - new_source) < 4 for m in self.all_darkrooms):
                    # Try not to put clusters too close together
                    darkness_sources.append(new_source)
                    new_source = darkness_sources.pop(0)
                new_cluster.append(new_source)
                self.all_darkrooms.append(new_source)
                # Spread to a random size between max/2 and max (or to the room cap or its boundary)
                new_cluster_size = random.randint(1 + int(max_cluster_size / 2), max_cluster_size)
                while (len(new_cluster) <= new_cluster_size) and (len(self.all_darkrooms) < self.max_darkrooms):
                    if not self.dr_spread_once(new_cluster):
                        break  # The cluster hit a wall (e.g. a type-1 room if uncursed) and can't grow
                # We're done with this cluster
                darkness_clusters.append(new_cluster)
        # If uncursed, add logic edges for darkness
        if not self.darkroom_cursed:
            dark_nodes = [n for n in self.graph if
                          any(darkroom == self.graph[n][3][3] for darkroom in self.all_darkrooms)]
            dark_exits = [x for x in self.exits if self.exits[x][3] in dark_nodes]
            for exit in dark_exits:
                new_logic_id = 1 + max(self.exit_logic)
                new_logic = [exit, [[28, 1], [39, 1]], 2, False]  # Dark Glasses, Crystal Ring
                self.exit_logic[new_logic_id] = new_logic

    # Returns a list of non-dark rooms that darkness can spread to from cluster, of requested or default types.
    def dr_get_nondark_sinks(self, cluster, types):
        if not types:
            if not self.darkroom_cursed:
                types = [2, 3, 4]
            else:
                types = [1, 2, 3, 4]
        return [sink for src in cluster for sink in self.maps[src][9] if
                self.maps[sink][4] in types and sink not in self.all_darkrooms]

    # Expands the darkness cluster into all adjacent rooms that inherit darkness.
    def dr_spread_to_free_sinks(self, cluster):
        new_free_sinks = [0]
        while new_free_sinks:
            new_free_sinks = self.dr_get_nondark_sinks(cluster, [4])
            cluster.extend(new_free_sinks)
            self.all_darkrooms.extend(new_free_sinks)

    # Expands the darkness cluster by one room (plus any adjacent free sinks).
    def dr_spread_once(self, cluster):
        self.dr_spread_to_free_sinks(cluster)
        all_sinks = self.dr_get_nondark_sinks(cluster, [])
        if not all_sinks:
            return False
        random.shuffle(all_sinks)
        new_room = all_sinks.pop()
        self.all_darkrooms.append(new_room)
        cluster.append(new_room)
        self.dr_spread_to_free_sinks(cluster)
        return True

    # Shuffle travel destinations
    def shuffle_overworld(self):
        new_continents = [[], [], [], [], []]

        # Ensure each continent has at least one travel location
        destination_list = [1, 6, 12, 14, 16, 18]
        random.shuffle(destination_list)
        for continent in new_continents:
            continent.append(destination_list.pop(0))

        # Randomly assign the rest of the locations
        destination_list += [2, 3, 4, 5, 7, 8, 9, 10, 11, 13, 15, 17, 19]
        random.shuffle(destination_list)
        new_continents[0] += destination_list[:4]
        new_continents[1] += destination_list[4:8]
        new_continents[2] += destination_list[8:10]
        new_continents[3] += destination_list[10:13]
        new_continents[4] += destination_list[-1:]
        for continent in new_continents:
            random.shuffle(continent)

        OVERWORLD_MENUS[1][0] = new_continents[0][0]
        OVERWORLD_MENUS[2][0] = new_continents[0][1]
        OVERWORLD_MENUS[3][0] = new_continents[0][2]
        OVERWORLD_MENUS[4][0] = new_continents[0][3]
        OVERWORLD_MENUS[5][0] = new_continents[0][4]
        OVERWORLD_MENUS[6][0] = new_continents[1][0]
        OVERWORLD_MENUS[7][0] = new_continents[1][1]
        OVERWORLD_MENUS[8][0] = new_continents[1][2]
        OVERWORLD_MENUS[9][0] = new_continents[1][3]
        OVERWORLD_MENUS[10][0] = new_continents[1][4]
        OVERWORLD_MENUS[11][0] = new_continents[2][0]
        OVERWORLD_MENUS[12][0] = new_continents[2][1]
        OVERWORLD_MENUS[13][0] = new_continents[2][2]
        OVERWORLD_MENUS[14][0] = new_continents[3][0]
        OVERWORLD_MENUS[15][0] = new_continents[3][1]
        OVERWORLD_MENUS[16][0] = new_continents[3][2]
        OVERWORLD_MENUS[17][0] = new_continents[3][3]
        OVERWORLD_MENUS[18][0] = new_continents[4][0]
        OVERWORLD_MENUS[19][0] = new_continents[4][1]

        self.graph[10][1].clear()
        self.graph[11][1].clear()
        self.graph[12][1].clear()
        self.graph[13][1].clear()
        self.graph[14][1].clear()

        self.graph[10][10].clear()
        self.graph[11][10].clear()
        self.graph[12][10].clear()
        self.graph[13][10].clear()
        self.graph[14][10].clear()

        # Add new overworld to the graph
        for entry in OVERWORLD_MENUS:
            new_entry = OVERWORLD_MENUS[entry][0]
            self.graph[OVERWORLD_MENUS[entry][2]][1].append(OVERWORLD_MENUS[new_entry][3])
            self.graph[OVERWORLD_MENUS[new_entry][3]][1].remove(OVERWORLD_MENUS[new_entry][2])
            self.graph[OVERWORLD_MENUS[new_entry][3]][1].append(OVERWORLD_MENUS[entry][2])

        return True

    # Check whether this monster ID is compatible with this enemy type.
    def can_monster_be_type(self, monster_id, enemy_type):
        if monster_id in ENEMIZER_RESTRICTED_ENEMIES:
            if enemy_type in ENEMIZER_RESTRICTED_ENEMIES[monster_id]:
                return False
        return True

    # Shuffle enemies in ROM
    def enemize(self):
        complex_enemies = [4, 15, 53, 62, 88]  # Enemies with many sprites, or are no fun
        max_complex = 5

        # Get list of enemysets
        enemysets = []
        for set in ENEMY_SETS:
            enemysets.append(set)

        # Shuffle enemy stats in Insane
        if self.enemizer == "Insane":
            insane_enemies = []
            insane_templates = []
            for enemy in ENEMIES:
                if ENEMIES[enemy][5] and enemy != 102:  # Special exception for Zombies
                    insane_enemies.append(enemy)
                    insane_templates.append(ENEMIES[enemy][2])

            random.shuffle(insane_templates)
            insane_dictionary = {}
            i = 0

            for enemy in insane_enemies:
                insane_dictionary[enemy] = insane_templates[i]
                i += 1

        # Randomize enemy spritesets
        for map in self.maps:
            if self.maps[map][0] < 0:
                continue
            complex_ct = 0
            oldset = self.maps[map][0]
            # Determine new enemyset for map
            if self.enemizer == "Limited":
                sets = [oldset]
            else:
                sets = [set for set in enemysets if set not in self.maps[map][7]]

            random.shuffle(sets)
            newset = sets[0]

            # Gather enemies from old and new sets
            old_enemies = []
            new_enemies = []
            for enemy in ENEMIES:
                if ENEMIES[enemy][0] == oldset:
                    old_enemies.append(enemy)
                if ENEMIES[enemy][0] == newset and ENEMIES[enemy][5]:
                    new_enemies.append(enemy)

            # Update map header to reflect new enemyset
            self.asar_defines["Map" + format(map, "02X") + "CardMonsters"] = "!" + ENEMY_SETS[newset][0]

            # Randomize each enemy in map
            first_monster_id = self.maps[map][5]
            last_monster_id = self.maps[map][6]
            this_monster_id = first_monster_id
            while this_monster_id <= last_monster_id:
                if this_monster_id not in DEFAULT_ENEMIES:
                    this_monster_id += 1
                    continue
                old_enemy = DEFAULT_ENEMIES[this_monster_id]
                enemytype = ENEMIES[old_enemy][3]
                walkable = ENEMIES[old_enemy][4]

                random.shuffle(new_enemies)
                i = 0
                found_enemy = False
                while not found_enemy:
                    new_enemy = new_enemies[i]
                    new_enemytype = ENEMIES[new_enemy][3]
                    new_walkable = ENEMIES[new_enemy][4]
                    if (i == len(new_enemies) - 1) or (
                            this_monster_id in ENEMIZER_RESTRICTED_ENEMIES and self.can_monster_be_type(
                        this_monster_id, new_enemy)) or (
                            (this_monster_id not in ENEMIZER_RESTRICTED_ENEMIES) and (
                            complex_ct < max_complex or new_enemy not in complex_enemies) and (
                                    walkable or new_enemytype == 3 or walkable == new_walkable)):
                        found_enemy = True
                        # Limit number of complex enemies per map
                        if new_enemy in complex_enemies:
                            complex_ct += 1
                    i += 1
                self.asar_defines["Monster" + format(this_monster_id, "04X") + "Addr"] = "!" + ENEMIES[new_enemy][
                    1]
                if map == 27:  # Moon Tribe doesn't shuffle stats
                    new_enemy_stat_block = ENEMIES[old_enemy][2]
                elif self.enemizer == "Balanced":  # Balanced enemizer doesn't shuffle stats--
                    new_enemy_stat_block = ENEMIES[old_enemy][2]
                    if old_enemy == 102:  # --except that we use the cyclops stat block for replaced zombies
                        new_enemy_stat_block = 0x47
                elif self.enemizer == "Insane" and new_enemy != 102:  # Insane uses random stat blocks for non-zombies
                    new_enemy_stat_block = insane_dictionary[new_enemy]
                else:  # Otherwise (Limited, Full, and zombies in Insane) the new monster uses its normal stat block
                    new_enemy_stat_block = ENEMIES[new_enemy][2]
                self.asar_defines["Monster" + format(this_monster_id, "04X") + "Stats"] = new_enemy_stat_block

                # Nearly all monsters use Param to set layer priority (o = $00/$10/$20/$30),
                # so should not override the Param (priority) of the monster they're replacing.
                # Wat wall skulls use Param = 0/2/4/6 to set their movement direction.
                # Inca statues with Param > 0 are frozen until a certain flag is set.
                # So for wall skulls we want Param = a random direction, for Inca statues we want Param = 0,
                # and for others we want to retain the priority bits but zero out the wall skull bits.
                if new_enemy == 108:
                    self.asar_defines["Monster" + format(this_monster_id, "04X") + "Param"] = random.randint(0, 3) * 2
                elif new_enemy in [16, 17, 18, 19, 20, 21, 22]:
                    self.asar_defines["Monster" + format(this_monster_id, "04X") + "Param"] = 0
                else:
                    self.asar_defines[
                        "Monster" + format(this_monster_id, "04X") + "Param"] = "!DefaultMonster" + format(
                        this_monster_id, "04X") + "Param&$F0"

                this_monster_id += 1

    # Build world
    def __init__(
        self, settings: RandomizerData, statues_required=6, statues=[1, 2, 3, 4, 5, 6],
        statue_req=StatueReq.GAME_CHOICE.value, kara=3, gem=[3, 5, 8, 12, 20, 30, 50], incatile=[9, 5],
        hieroglyphs=[1, 2, 3, 4, 5, 6], boss_order=[1, 2, 3, 4, 5, 6, 7]
    ):
        self.errorlog = []
        self.seed = settings.seed
        self.race_mode = settings.race_mode
        self.statues = statues
        self.statues_required = statues_required
        self.statue_req = statue_req
        self.boss_order = boss_order
        self.dungeons_req = []
        for x in self.statues:
            self.dungeons_req.append(self.boss_order[x - 1])

        gaia_coinflip = random.randint(0, 1)
        if settings.goal.value == Goal.RED_JEWEL_HUNT.value:
            self.goal = "Red Jewel Hunt"
        elif settings.goal.value == Goal.APO_GAIA.value or (
                settings.goal.value == Goal.RANDOM_GAIA.value and gaia_coinflip):
            self.goal = "Apocalypse Gaia"
        else:
            self.goal = "Dark Gaia"

        if settings.logic.value == Logic.COMPLETABLE.value:
            self.logic_mode = "Completable"
        elif settings.logic.value == Logic.BEATABLE.value:
            self.logic_mode = "Beatable"
        else:
            self.logic_mode = "Chaos"

        if settings.town_shuffle or settings.dungeon_shuffle:
            self.entrance_shuffle = True
        else:
            self.entrance_shuffle = False
        self.coupled_exits = settings.coupled_exits
        self.town_shuffle = settings.town_shuffle
        self.dungeon_shuffle = settings.dungeon_shuffle

        if settings.flute.value == FluteOpt.START.value:
            self.flute = "Start"
        elif settings.flute.value == FluteOpt.SHUFFLE.value:
            self.flute = "Shuffle"
        else:
            self.flute = "Fluteless"

        # if settings.orb_rando.value == OrbRando.NONE.value:
        #    self.orb_rando = "None"
        # elif settings.orb_rando.value == OrbRando.BASIC.value:
        #    self.orb_rando = "Basic"
        # else:
        #    self.orb_rando = "Orbsanity"
        self.orb_rando = "Orbsanity" if settings.orb_rando else "None"

        if abs(settings.darkrooms.value) == DarkRooms.NONE.value:
            self.darkroom_level = "None"
        elif abs(settings.darkrooms.value) == DarkRooms.FEW.value:
            self.darkroom_level = "Few"
        elif abs(settings.darkrooms.value) == DarkRooms.SOME.value:
            self.darkroom_level = "Some"
        elif abs(settings.darkrooms.value) == DarkRooms.MANY.value:
            self.darkroom_level = "Many"
        elif abs(settings.darkrooms.value) == DarkRooms.ALL.value:
            self.darkroom_level = "All"
        if settings.darkrooms.value >= 0:
            self.darkroom_cursed = False
        else:
            self.darkroom_cursed = True

        # if settings.dungeon_shuffle.value == DungeonShuffle.NONE.value:
        #    self.dungeon_shuffle = "None"
        # elif settings.dungeon_shuffle.value == DungeonShuffle.BASIC.value:
        #    self.dungeon_shuffle = "Basic"
        # elif settings.dungeon_shuffle.value == DungeonShuffle.CHAOS.value:
        #    self.dungeon_shuffle = "Chaos"
        # elif settings.dungeon_shuffle.value == DungeonShuffle.CLUSTERED.value:
        #    self.dungeon_shuffle = "Clustered"

        if settings.start_location.value == StartLocation.SOUTH_CAPE.value:
            self.start_mode = "South Cape"
        elif settings.start_location.value == StartLocation.SAFE.value:
            self.start_mode = "Safe"
        elif settings.start_location.value == StartLocation.UNSAFE.value:
            self.start_mode = "Unsafe"
        else:
            self.start_mode = "Forced Unsafe"

        if settings.enemizer.value == Enemizer.NONE.value:
            self.enemizer = "None"
        elif settings.enemizer.value == Enemizer.BALANCED.value:
            self.enemizer = "Balanced"
        elif settings.enemizer.value == Enemizer.LIMITED.value:
            self.enemizer = "Limited"
        elif settings.enemizer.value == Enemizer.FULL.value:
            self.enemizer = "Full"
        else:
            self.enemizer = "Insane"

        if settings.ohko:
            self.variant = ["OHKO"]
        elif settings.red_jewel_madness:
            self.variant = ["RJM"]
        else:
            self.variant = []

        if settings.allow_glitches:
            self.variant.append("Allow Glitches")

        if settings.boss_shuffle:
            self.variant.append("Boss Shuffle")

        if settings.overworld_shuffle:
            self.variant.append("Overworld Shuffle")

        if settings.open_mode:
            self.variant.append("Open Mode")

        if settings.z3:
            self.variant.append("Z3 Mode")

        self.firebird = settings.firebird
        self.start_loc = 10
        #        self.level = settings.level.value
        self.difficulty = settings.difficulty.value
        self.kara = kara
        self.gem = gem
        self.incatile = incatile
        self.hieroglyphs = hieroglyphs
        self.placement_log = []
        self.exit_log = []
        self.spoilers = []
        self.base_item_counts = {}
        self.required_items = [20, 36]
        self.good_items = [10, 13, 24, 25, 37, 62, 63, 64]
        self.trolly_locations = [32, 45, 64, 65, 102, 108, 121, 128, 136, 147]
        self.free_locations = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 24, 33, 34, 35, 36, 37, 38, 39]
        self.optional_nodes = [-2, -1, 491, 600, 601, 602, 604, 605, 606, 607, 800, 801, 802, 803]  # Artificial nodes, not required by completable logic
        self.map_patches = []
        self.visited = []
        self.items_collected = []
        self.item_destinations = []
        self.open_locations = []  # Pool sublists are added to this in initialization
        self.open_edges = []
        self.graph_viz = None
        self.all_darkrooms = []
        self.max_darkrooms = 0
        self.asar_defines = {"DummyDefine": "DummyDefine"}

        dungeon_keys_nondroppable = []
        for x in [3, 5]:
            # Generally can't drop Ramas/Hieros/Journal if Gold Ship or passage to a new room might be behind them
            if x in self.dungeons_req or self.dungeon_shuffle or (self.boss_order != [1, 2, 3, 4, 5, 6, 7]):
                dungeon_keys_nondroppable.append(x)

        self.spawn_locations = get_spawn_locations(self.entrance_shuffle, self.dungeon_shuffle, self.difficulty, self.flute)

        self.deleted_item_pool = {}
        self.item_pool = get_item_pool(settings.infinite_inventory, self.variant, settings.orb_rando, self.difficulty, self.dungeon_shuffle, dungeon_keys_nondroppable, settings.darkrooms.value)

        self.deleted_item_locations = {}

        self.deleted_graph = {}

        # self.graph is modified. get_graph() is the basis but the intention is mutability
        self.graph = get_graph()
        self.maps = get_maps()
        self.item_locations = get_item_locations()

        self.deleted_logic = {}
        self.logic = get_logic(gem, self.goal, self.difficulty, self.dungeon_shuffle, self.coupled_exits, self.enemizer, self.statues_required, self.kara, settings.allow_glitches)

        self.area_short_name = get_area_short_name(self.kara)

        self.deleted_exits = {}
        self.exits = get_exits(self.goal, self.town_shuffle)

        self.exit_logic = get_exit_logic(settings.allow_glitches)

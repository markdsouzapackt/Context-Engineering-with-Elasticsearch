# Code example from Context Engineering with Elasticsearch book
# Copyright 2026 by Enrico Zimuel. All rights reserved.

# This module provides functions to format Elasticsearch profile responses into human-readable Markdown.

def format_nanos(value):
    """Return nanoseconds plus milliseconds for easier reading."""
    return f"{value:,} ns ({value / 1_000_000:.3f} ms)"


def node_label(node):
    node_type = node.get("type") or node.get("name") or "unknown"
    time_in_nanos = node.get("time_in_nanos")

    if time_in_nanos is None:
        return node_type

    return f"{node_type} [{format_nanos(time_in_nanos)}]"


def print_node_tree(node, prefix="", is_last=True):
    connector = "└── " if is_last else "├── "
    child_prefix = "    " if is_last else "│   "

    print(prefix + connector + node_label(node))

    description = node.get("description")
    if description:
        print(prefix + child_prefix + f"description: {description}")

    reason = node.get("reason")
    if reason:
        print(prefix + child_prefix + f"reason: {reason}")

    debug = node.get("debug")
    if debug:
        print(prefix + child_prefix + "debug:")
        debug_items = list(debug.items())
        for index, (key, value) in enumerate(debug_items):
            debug_connector = "└── " if index == len(debug_items) - 1 else "├── "
            print(prefix + child_prefix + debug_connector + f"{key}: {value}")

    children = node.get("children", [])
    for index, child in enumerate(children):
        print_node_tree(
            child,
            prefix=prefix + child_prefix,
            is_last=index == len(children) - 1,
        )


def print_profile_tree(profile):
    shards = profile.get("shards", [])

    print("Elasticsearch profile")

    for shard_index, shard in enumerate(shards):
        shard_is_last = shard_index == len(shards) - 1
        shard_connector = "└── " if shard_is_last else "├── "
        shard_prefix = "    " if shard_is_last else "│   "

        print(f"{shard_connector}Shard {shard_index + 1}: {shard.get('index')}")
        print(f"{shard_prefix}├── id: {shard.get('id')}")
        print(f"{shard_prefix}├── node_id: {shard.get('node_id')}")
        print(f"{shard_prefix}├── shard_id: {shard.get('shard_id')}")
        print(f"{shard_prefix}├── cluster: {shard.get('cluster')}")

        sections = []

        searches = shard.get("searches", [])
        if searches:
            sections.append(("Searches", searches))

        fetch = shard.get("fetch")
        if fetch:
            sections.append(("Fetch", [fetch]))

        for section_index, (section_name, items) in enumerate(sections):
            section_is_last = section_index == len(sections) - 1
            section_connector = "└── " if section_is_last else "├── "
            section_prefix = "    " if section_is_last else "│   "

            print(f"{shard_prefix}{section_connector}{section_name}")

            if section_name == "Searches":
                for search_index, search in enumerate(items):
                    search_is_last = (
                        search_index == len(items) - 1
                        and "collector" not in search
                    )
                    search_connector = "└── " if search_is_last else "├── "
                    search_prefix = section_prefix + ("    " if search_is_last else "│   ")

                    print(
                        f"{shard_prefix}{section_prefix}"
                        f"{search_connector}Search {search_index + 1}"
                    )

                    query_nodes = search.get("query", [])
                    for query_index, query_node in enumerate(query_nodes):
                        print_node_tree(
                            query_node,
                            prefix=shard_prefix + search_prefix,
                            is_last=False,
                        )

                    collector_nodes = search.get("collector", [])
                    if collector_nodes:
                        print(f"{shard_prefix}{search_prefix}├── Collectors")
                        for collector_index, collector_node in enumerate(collector_nodes):
                            print_node_tree(
                                collector_node,
                                prefix=shard_prefix + search_prefix + "│   ",
                                is_last=collector_index == len(collector_nodes) - 1,
                            )

                    rewrite_time = search.get("rewrite_time")
                    if rewrite_time is not None:
                        print(
                            f"{shard_prefix}{search_prefix}└── "
                            f"rewrite_time: {format_nanos(rewrite_time)}"
                        )

            elif section_name == "Fetch":
                for item_index, item in enumerate(items):
                    print_node_tree(
                        item,
                        prefix=shard_prefix + section_prefix,
                        is_last=item_index == len(items) - 1,
                    )
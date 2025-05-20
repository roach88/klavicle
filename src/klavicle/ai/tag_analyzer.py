import re
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Set

from rich.console import Console
from rich.table import Table


class TagAnalyzer:
    """
    Aggregates and analyzes tags across campaigns, flows, and lists.
    Provides insights on tag usage, duplication, naming consistency, and cross-entity patterns.
    """

    def __init__(self):
        self.console = Console()

    def aggregate_tags(
        self,
        campaigns: Optional[List[Dict[str, Any]]] = None,
        flows: Optional[List[Dict[str, Any]]] = None,
        lists_: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, List[str]]:
        """
        Aggregate tags from campaigns, flows, and lists.
        Returns a dict with keys 'campaigns', 'flows', 'lists', and 'all'.
        """
        tag_map = {"campaigns": [], "flows": [], "lists": []}
        if campaigns:
            tag_map["campaigns"] = [tag for c in campaigns for tag in c.get("tags", [])]
        if flows:
            tag_map["flows"] = [tag for f in flows for tag in f.get("tags", [])]
        if lists_:
            tag_map["lists"] = [tag for l in lists_ for tag in l.get("tags", [])]
        tag_map["all"] = tag_map["campaigns"] + tag_map["flows"] + tag_map["lists"]
        return tag_map

    def tag_frequency(self, tag_map: Dict[str, List[str]]) -> Dict[str, Counter]:
        """
        Count tag frequency for each entity type and overall.
        Returns a dict of Counters.
        """
        return {k: Counter(v) for k, v in tag_map.items()}

    def find_duplicates(self, tag_map: Dict[str, List[str]]) -> Set[str]:
        """
        Find tags that appear in more than one entity type.
        """
        sets = [set(tag_map[k]) for k in ("campaigns", "flows", "lists")]
        return set.intersection(*sets) if all(sets) else set()

    def find_unused(
        self,
        tag_map: Dict[str, List[str]],
        all_possible_tags: Optional[Set[str]] = None,
    ) -> Set[str]:
        """
        Find tags that are defined but not used (if all_possible_tags is provided).
        """
        if not all_possible_tags:
            return set()
        used = set(tag_map["all"])
        return all_possible_tags - used

    def check_naming_consistency(self, tags: List[str]) -> Dict[str, List[str]]:
        """
        Check for inconsistent naming (case, format, delimiters, etc.).
        Returns a dict with keys for issues and lists of problematic tags.
        """
        issues = defaultdict(list)
        for tag in tags:
            if tag != tag.lower():
                issues["case"].append(tag)
            if not re.match(r"^[a-z0-9_\-:]+$", tag):
                issues["format"].append(tag)
            if ":" not in tag:
                issues["missing_colon"].append(tag)
        return dict(issues)

    def cross_entity_analysis(self, tag_map: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Analyze tag usage across entities for consistency and overlap.
        Returns a dict with overlap, unique tags, and entity-specific tags.
        """
        sets = {k: set(v) for k, v in tag_map.items() if k != "all"}
        overlap = set.intersection(*sets.values()) if sets else set()
        unique = {
            k: sets[k] - set.union(*(sets[j] for j in sets if j != k)) for k in sets
        }
        return {"overlap": overlap, "unique": unique}

    def summary_report(self, tag_map: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Generate a summary report of tag usage and recommendations.
        """
        freq = self.tag_frequency(tag_map)
        duplicates = self.find_duplicates(tag_map)
        naming_issues = self.check_naming_consistency(tag_map["all"])
        cross_entity = self.cross_entity_analysis(tag_map)
        return {
            "tag_frequency": {k: dict(v) for k, v in freq.items()},
            "duplicates": list(duplicates),
            "naming_issues": naming_issues,
            "cross_entity": cross_entity,
            "recommendations": self.recommendations(
                freq, duplicates, naming_issues, cross_entity
            ),
        }

    def recommendations(
        self, freq, duplicates, naming_issues, cross_entity
    ) -> List[str]:
        """
        Generate actionable recommendations based on analysis.
        """
        recs = []
        if duplicates:
            recs.append(
                f"Consider consolidating duplicate tags used across entities: {', '.join(duplicates)}"
            )
        if naming_issues.get("case"):
            recs.append(
                f"Normalize tag case to lowercase: {', '.join(naming_issues['case'])}"
            )
        if naming_issues.get("format"):
            recs.append(
                f"Fix tag format to use only a-z, 0-9, _, -, or : {', '.join(naming_issues['format'])}"
            )
        if naming_issues.get("missing_colon"):
            recs.append(
                f"Adopt a category:value format for tags: {', '.join(naming_issues['missing_colon'])}"
            )
        for entity, tags in cross_entity["unique"].items():
            if tags:
                recs.append(f"Tags unique to {entity}: {', '.join(tags)}")
        if not recs:
            recs.append("Tag usage is consistent and well-structured.")
        return recs

    def print_tag_analysis(self, report: Dict[str, Any]) -> None:
        """
        Print a summary of tag analysis to the console.
        """
        self.console.print("\n[bold blue]Tag Analysis Summary[/bold blue]")
        freq = report["tag_frequency"]
        table = Table(title="Tag Frequency by Entity")
        table.add_column("Entity")
        table.add_column("Tag")
        table.add_column("Count", justify="right")
        for entity in ("campaigns", "flows", "lists"):
            for tag, count in freq[entity].items():
                table.add_row(entity, tag, str(count))
        self.console.print(table)
        if report["duplicates"]:
            self.console.print(
                f"\n[bold yellow]Duplicate tags across entities:[/bold yellow] {', '.join(report['duplicates'])}"
            )
        if report["naming_issues"]:
            self.console.print(
                f"\n[bold red]Naming issues:[/bold red] {report['naming_issues']}"
            )
        if report["cross_entity"]:
            self.console.print(
                f"\n[bold green]Cross-entity analysis:[/bold green] {report['cross_entity']}"
            )
        if report["recommendations"]:
            self.console.print("\n[bold magenta]Recommendations:[/bold magenta]")
            for rec in report["recommendations"]:
                self.console.print(f"- {rec}")

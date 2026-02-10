"""
Dependency Mapper Engine
Visualizes and analyzes application interconnections and dependencies
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from collections import defaultdict
from datetime import datetime
import uuid


@dataclass
class DependencyNode:
    """Represents an application node in the dependency graph"""
    app_id: str
    app_name: str
    category: str = "unknown"
    time_category: str = "unknown"
    composite_score: float = 0.0
    criticality: str = "medium"
    dependencies: List[str] = field(default_factory=list)  # Apps this depends on
    dependents: List[str] = field(default_factory=list)    # Apps that depend on this


@dataclass
class DependencyEdge:
    """Represents a dependency relationship between two applications"""
    source_id: str
    target_id: str
    dependency_type: str = "data"  # data, api, auth, shared_db, file_transfer
    criticality: str = "medium"    # critical, high, medium, low
    direction: str = "downstream"  # downstream, upstream, bidirectional
    description: str = ""


@dataclass
class BlastRadiusResult:
    """Result of blast radius analysis"""
    app_id: str
    app_name: str
    direct_impact_count: int
    indirect_impact_count: int
    total_impact_count: int
    impacted_apps: List[Dict[str, Any]]
    risk_level: str
    estimated_downtime_hours: float
    recommendations: List[str]


@dataclass
class CriticalPath:
    """Represents a critical path through the application portfolio"""
    path_id: str
    path_name: str
    apps: List[str]
    total_length: int
    weakest_link_app: str
    weakest_link_score: float
    risk_level: str
    description: str


class DependencyMapper:
    """
    Maps and analyzes application dependencies within a portfolio.

    Features:
    - Build dependency graph from application metadata
    - Identify circular dependencies
    - Calculate blast radius for each application
    - Find critical paths through the portfolio
    - Generate visualization data for D3.js/Cytoscape
    """

    # Dependency types and their risk multipliers
    DEPENDENCY_TYPES = {
        'api': {'risk_multiplier': 1.0, 'description': 'API/Web Service'},
        'database': {'risk_multiplier': 1.5, 'description': 'Shared Database'},
        'file_transfer': {'risk_multiplier': 0.8, 'description': 'File Transfer/ETL'},
        'authentication': {'risk_multiplier': 1.3, 'description': 'Authentication/SSO'},
        'messaging': {'risk_multiplier': 0.9, 'description': 'Message Queue'},
        'data_sync': {'risk_multiplier': 1.1, 'description': 'Data Synchronization'},
        'embedded': {'risk_multiplier': 1.8, 'description': 'Embedded/Tightly Coupled'},
        'reporting': {'risk_multiplier': 0.6, 'description': 'Reporting/Analytics'}
    }

    # Criticality levels
    CRITICALITY_LEVELS = ['critical', 'high', 'medium', 'low']

    def __init__(self):
        self.nodes: Dict[str, DependencyNode] = {}
        self.edges: List[DependencyEdge] = []
        self.adjacency_list: Dict[str, List[str]] = defaultdict(list)
        self.reverse_adjacency: Dict[str, List[str]] = defaultdict(list)

    def build_graph(self, applications: List[Dict]) -> Dict[str, Any]:
        """
        Build dependency graph from application list.

        Args:
            applications: List of application dicts with dependencies field

        Returns:
            Graph summary with nodes, edges, and metrics
        """
        self.nodes.clear()
        self.edges.clear()
        self.adjacency_list.clear()
        self.reverse_adjacency.clear()

        # Create nodes
        for app in applications:
            app_id = str(app.get('id', ''))
            node = DependencyNode(
                app_id=app_id,
                app_name=app.get('name', 'Unknown'),
                category=app.get('category', 'unknown'),
                time_category=app.get('time_category', 'unknown'),
                composite_score=app.get('composite_score', 0.0),
                criticality=self._infer_criticality(app),
                dependencies=app.get('dependencies', []),
                dependents=[]
            )
            self.nodes[app_id] = node

        # Build edges from dependencies
        for app_id, node in self.nodes.items():
            for dep_id in node.dependencies:
                if dep_id in self.nodes:
                    # Create edge
                    edge = DependencyEdge(
                        source_id=app_id,
                        target_id=dep_id,
                        dependency_type=self._infer_dependency_type(
                            self.nodes[app_id], self.nodes[dep_id]
                        ),
                        criticality=self._calculate_edge_criticality(
                            self.nodes[app_id], self.nodes[dep_id]
                        )
                    )
                    self.edges.append(edge)

                    # Update adjacency lists
                    self.adjacency_list[app_id].append(dep_id)
                    self.reverse_adjacency[dep_id].append(app_id)

                    # Update dependents
                    self.nodes[dep_id].dependents.append(app_id)

        return self.get_graph_summary()

    def _infer_criticality(self, app: Dict) -> str:
        """Infer application criticality from attributes"""
        score = app.get('composite_score', 50)
        business_value = app.get('business_value', 5)

        if business_value >= 8 or app.get('mission_critical', False):
            return 'critical'
        elif score >= 70 or business_value >= 6:
            return 'high'
        elif score >= 40 or business_value >= 4:
            return 'medium'
        return 'low'

    def _infer_dependency_type(self, source: DependencyNode, target: DependencyNode) -> str:
        """Infer dependency type from application categories"""
        source_cat = source.category.lower()
        target_cat = target.category.lower()

        if 'database' in source_cat or 'database' in target_cat:
            return 'database'
        elif 'auth' in source_cat or 'identity' in target_cat:
            return 'authentication'
        elif 'analytics' in source_cat or 'report' in target_cat:
            return 'reporting'
        elif 'etl' in source_cat or 'integration' in target_cat:
            return 'file_transfer'
        return 'api'

    def _calculate_edge_criticality(self, source: DependencyNode, target: DependencyNode) -> str:
        """Calculate criticality of a dependency edge"""
        if source.criticality == 'critical' or target.criticality == 'critical':
            return 'critical'
        elif source.criticality == 'high' or target.criticality == 'high':
            return 'high'
        elif source.criticality == 'medium' and target.criticality == 'medium':
            return 'medium'
        return 'low'

    def get_graph_summary(self) -> Dict[str, Any]:
        """Get summary statistics for the dependency graph"""
        if not self.nodes:
            return {'nodes': [], 'edges': [], 'metrics': {}}

        # Calculate metrics
        total_dependencies = len(self.edges)
        avg_dependencies = total_dependencies / len(self.nodes) if self.nodes else 0

        # Find highly connected apps
        connection_counts = {
            app_id: len(self.adjacency_list[app_id]) + len(self.reverse_adjacency[app_id])
            for app_id in self.nodes
        }
        highly_connected = sorted(
            connection_counts.items(), key=lambda x: x[1], reverse=True
        )[:5]

        # Find isolated apps
        isolated = [
            app_id for app_id, count in connection_counts.items() if count == 0
        ]

        return {
            'nodes': [
                {
                    'id': node.app_id,
                    'name': node.app_name,
                    'category': node.category,
                    'time_category': node.time_category,
                    'composite_score': node.composite_score,
                    'criticality': node.criticality,
                    'dependency_count': len(node.dependencies),
                    'dependent_count': len(node.dependents)
                }
                for node in self.nodes.values()
            ],
            'edges': [
                {
                    'source': edge.source_id,
                    'target': edge.target_id,
                    'type': edge.dependency_type,
                    'criticality': edge.criticality
                }
                for edge in self.edges
            ],
            'metrics': {
                'total_nodes': len(self.nodes),
                'total_edges': total_dependencies,
                'average_dependencies': round(avg_dependencies, 2),
                'highly_connected_apps': [
                    {'id': app_id, 'name': self.nodes[app_id].app_name, 'connections': count}
                    for app_id, count in highly_connected
                ],
                'isolated_apps': [
                    {'id': app_id, 'name': self.nodes[app_id].app_name}
                    for app_id in isolated
                ],
                'circular_dependencies': self.find_circular_dependencies()
            }
        }

    def find_circular_dependencies(self) -> List[List[str]]:
        """Find all circular dependencies in the graph using DFS"""
        cycles = []
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node_id: str):
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)

            for neighbor in self.adjacency_list[node_id]:
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append([
                        self.nodes[app_id].app_name for app_id in cycle
                    ])

            path.pop()
            rec_stack.remove(node_id)

        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id)

        return cycles

    def calculate_blast_radius(self, app_id: str) -> BlastRadiusResult:
        """
        Calculate the blast radius if an application fails/is retired.

        Returns apps that would be directly and indirectly affected.
        """
        if app_id not in self.nodes:
            return BlastRadiusResult(
                app_id=app_id,
                app_name="Unknown",
                direct_impact_count=0,
                indirect_impact_count=0,
                total_impact_count=0,
                impacted_apps=[],
                risk_level="unknown",
                estimated_downtime_hours=0,
                recommendations=[]
            )

        node = self.nodes[app_id]

        # BFS to find all affected apps
        direct_affected = set(self.reverse_adjacency[app_id])
        all_affected = set()
        queue = list(direct_affected)

        while queue:
            current = queue.pop(0)
            if current not in all_affected:
                all_affected.add(current)
                queue.extend(self.reverse_adjacency[current])

        indirect_affected = all_affected - direct_affected

        # Build impacted apps list
        impacted_apps = []
        for affected_id in all_affected:
            if affected_id in self.nodes:
                affected_node = self.nodes[affected_id]
                impacted_apps.append({
                    'id': affected_id,
                    'name': affected_node.app_name,
                    'impact_type': 'direct' if affected_id in direct_affected else 'indirect',
                    'criticality': affected_node.criticality
                })

        # Calculate risk level
        critical_count = sum(1 for a in impacted_apps if a['criticality'] == 'critical')
        high_count = sum(1 for a in impacted_apps if a['criticality'] == 'high')

        if critical_count >= 2 or len(all_affected) >= 10:
            risk_level = 'critical'
        elif critical_count >= 1 or high_count >= 3:
            risk_level = 'high'
        elif len(all_affected) >= 3:
            risk_level = 'medium'
        else:
            risk_level = 'low'

        # Estimate downtime
        base_hours = 4 if node.criticality == 'critical' else 2
        estimated_downtime = base_hours + (len(all_affected) * 0.5)

        # Generate recommendations
        recommendations = self._generate_blast_radius_recommendations(
            node, impacted_apps, risk_level
        )

        return BlastRadiusResult(
            app_id=app_id,
            app_name=node.app_name,
            direct_impact_count=len(direct_affected),
            indirect_impact_count=len(indirect_affected),
            total_impact_count=len(all_affected),
            impacted_apps=impacted_apps,
            risk_level=risk_level,
            estimated_downtime_hours=round(estimated_downtime, 1),
            recommendations=recommendations
        )

    def _generate_blast_radius_recommendations(
        self, node: DependencyNode, impacted: List[Dict], risk_level: str
    ) -> List[str]:
        """Generate recommendations based on blast radius analysis"""
        recommendations = []

        if risk_level in ['critical', 'high']:
            recommendations.append(
                f"High-risk dependency hub: Consider implementing failover mechanisms for {node.app_name}"
            )
            recommendations.append(
                "Create detailed disaster recovery plan before any changes"
            )

        if len(impacted) > 5:
            recommendations.append(
                "Multiple downstream dependencies: Implement circuit breakers to prevent cascade failures"
            )

        critical_apps = [a for a in impacted if a['criticality'] == 'critical']
        if critical_apps:
            names = ', '.join(a['name'] for a in critical_apps[:3])
            recommendations.append(
                f"Critical systems affected: Ensure {names} have redundancy"
            )

        if node.time_category == 'Eliminate':
            recommendations.append(
                "Retirement planned: Create migration path for dependent applications first"
            )

        return recommendations

    def find_critical_paths(self) -> List[CriticalPath]:
        """Identify critical paths through the application portfolio"""
        critical_paths = []

        # Find apps with no dependencies (entry points)
        entry_points = [
            app_id for app_id in self.nodes
            if not self.adjacency_list[app_id]
        ]

        # Find apps with no dependents (exit points)
        exit_points = [
            app_id for app_id in self.nodes
            if not self.reverse_adjacency[app_id]
        ]

        # DFS to find all paths
        def find_paths(start: str, end: str, path: List[str], visited: Set[str]):
            if start == end:
                return [path]

            paths = []
            for next_node in self.reverse_adjacency[start]:
                if next_node not in visited:
                    visited.add(next_node)
                    new_paths = find_paths(next_node, end, path + [next_node], visited)
                    paths.extend(new_paths)
                    visited.remove(next_node)
            return paths

        # Find paths between entry and exit points (limit to prevent explosion)
        path_count = 0
        max_paths = 10

        for entry in entry_points[:5]:
            if path_count >= max_paths:
                break
            for exit_point in exit_points[:5]:
                if path_count >= max_paths:
                    break
                if entry != exit_point:
                    paths = find_paths(exit_point, entry, [exit_point], {exit_point})
                    for p in paths[:2]:  # Limit paths per pair
                        if len(p) >= 3:  # Only meaningful paths
                            # Find weakest link
                            min_score = float('inf')
                            weakest = p[0]
                            for app_id in p:
                                if app_id in self.nodes:
                                    score = self.nodes[app_id].composite_score
                                    if score < min_score:
                                        min_score = score
                                        weakest = app_id

                            # Determine risk level
                            if min_score < 30:
                                risk = 'critical'
                            elif min_score < 50:
                                risk = 'high'
                            elif min_score < 70:
                                risk = 'medium'
                            else:
                                risk = 'low'

                            critical_paths.append(CriticalPath(
                                path_id=str(uuid.uuid4())[:8],
                                path_name=f"{self.nodes[p[0]].app_name} → {self.nodes[p[-1]].app_name}",
                                apps=[self.nodes[a].app_name for a in p],
                                total_length=len(p),
                                weakest_link_app=self.nodes[weakest].app_name if weakest in self.nodes else 'Unknown',
                                weakest_link_score=min_score,
                                risk_level=risk,
                                description=f"Data flow path with {len(p)} applications"
                            ))
                            path_count += 1

        # Sort by risk level
        risk_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        critical_paths.sort(key=lambda x: risk_order.get(x.risk_level, 4))

        return critical_paths

    def get_visualization_data(self, layout: str = 'force') -> Dict[str, Any]:
        """
        Generate visualization data for D3.js or Cytoscape.js

        Args:
            layout: Graph layout algorithm (force, hierarchical, circular)
        """
        nodes = []
        for node in self.nodes.values():
            # Color coding by TIME category
            color_map = {
                'Invest': '#28a745',
                'Tolerate': '#ffc107',
                'Migrate': '#17a2b8',
                'Eliminate': '#dc3545',
                'unknown': '#6c757d'
            }

            # Size by number of connections
            connections = len(node.dependencies) + len(node.dependents)
            size = max(20, min(60, 20 + connections * 5))

            nodes.append({
                'id': node.app_id,
                'label': node.app_name,
                'category': node.category,
                'time_category': node.time_category,
                'score': node.composite_score,
                'criticality': node.criticality,
                'color': color_map.get(node.time_category, '#6c757d'),
                'size': size,
                'connections': connections
            })

        edges = []
        for edge in self.edges:
            # Line style by criticality
            style_map = {
                'critical': 'solid',
                'high': 'dashed',
                'medium': 'dotted',
                'low': 'dotted'
            }

            edges.append({
                'source': edge.source_id,
                'target': edge.target_id,
                'type': edge.dependency_type,
                'criticality': edge.criticality,
                'style': style_map.get(edge.criticality, 'dotted'),
                'label': self.DEPENDENCY_TYPES.get(edge.dependency_type, {}).get('description', edge.dependency_type)
            })

        return {
            'nodes': nodes,
            'edges': edges,
            'layout': layout,
            'legend': {
                'node_colors': {
                    'Invest': '#28a745',
                    'Tolerate': '#ffc107',
                    'Migrate': '#17a2b8',
                    'Eliminate': '#dc3545'
                },
                'edge_styles': {
                    'critical': 'Solid line',
                    'high': 'Dashed line',
                    'medium': 'Dotted line',
                    'low': 'Light dotted line'
                }
            }
        }

    def analyze_retirement_sequence(self, apps_to_retire: List[str]) -> Dict[str, Any]:
        """
        Determine the optimal sequence for retiring multiple applications.

        Returns ordered list with dependencies considered.
        """
        # Build retirement order based on dependencies
        ordered = []
        remaining = set(apps_to_retire)
        visited = set()

        while remaining:
            # Find apps with no dependents in the remaining set
            can_retire = []
            for app_id in remaining:
                dependents_in_set = [
                    d for d in self.reverse_adjacency.get(app_id, [])
                    if d in remaining
                ]
                if not dependents_in_set:
                    can_retire.append(app_id)

            if not can_retire:
                # Circular dependency - pick lowest score
                can_retire = [min(remaining, key=lambda x: self.nodes.get(x, DependencyNode(x, 'Unknown')).composite_score)]

            for app_id in can_retire:
                if app_id in self.nodes:
                    ordered.append({
                        'app_id': app_id,
                        'app_name': self.nodes[app_id].app_name,
                        'phase': len(ordered) // 3 + 1,  # Group into phases of 3
                        'dependent_count': len(self.reverse_adjacency.get(app_id, [])),
                        'notes': self._get_retirement_notes(app_id)
                    })
                remaining.discard(app_id)
                visited.add(app_id)

        return {
            'retirement_sequence': ordered,
            'total_apps': len(ordered),
            'phases': (len(ordered) // 3) + 1,
            'warnings': self._get_retirement_warnings(apps_to_retire)
        }

    def _get_retirement_notes(self, app_id: str) -> str:
        """Get retirement notes for an application"""
        if app_id not in self.nodes:
            return "Unknown application"

        node = self.nodes[app_id]
        dependents = self.reverse_adjacency.get(app_id, [])

        if not dependents:
            return "No dependencies - safe to retire"
        elif len(dependents) == 1:
            return f"1 dependent app: {self.nodes.get(dependents[0], DependencyNode('', 'Unknown')).app_name}"
        else:
            return f"{len(dependents)} dependent apps - coordinate retirement"

    def _get_retirement_warnings(self, apps: List[str]) -> List[str]:
        """Get warnings for batch retirement"""
        warnings = []

        critical_apps = [
            a for a in apps
            if a in self.nodes and self.nodes[a].criticality == 'critical'
        ]
        if critical_apps:
            warnings.append(f"{len(critical_apps)} critical applications in retirement list")

        # Check for circular deps among apps
        cycles = self.find_circular_dependencies()
        for cycle in cycles:
            cycle_ids = [
                app_id for app_id in self.nodes
                if self.nodes[app_id].app_name in cycle
            ]
            if any(a in apps for a in cycle_ids):
                warnings.append(f"Circular dependency detected: {' → '.join(cycle)}")

        return warnings


# Factory function
def create_dependency_mapper() -> DependencyMapper:
    """Create a new DependencyMapper instance"""
    return DependencyMapper()

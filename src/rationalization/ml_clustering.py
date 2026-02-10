"""
ML Clustering Engine for Application Rationalization Pro
Automatically groups applications based on similarity across multiple dimensions.

Features:
- K-Means clustering for application grouping
- Hierarchical clustering for dendrograms
- Silhouette analysis for optimal cluster count
- Cluster profiling with characteristic insights
- Consolidation opportunity detection
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from datetime import datetime
import math
import random
from collections import defaultdict


class ClusteringMethod(Enum):
    """Available clustering algorithms."""
    KMEANS = "kmeans"
    HIERARCHICAL = "hierarchical"
    DBSCAN = "dbscan"


class DistanceMetric(Enum):
    """Distance calculation methods."""
    EUCLIDEAN = "euclidean"
    MANHATTAN = "manhattan"
    COSINE = "cosine"


class ClusterCharacteristic(Enum):
    """Types of cluster characteristics."""
    HIGH_COST_LOW_VALUE = "high_cost_low_value"
    LEGACY_TECH_DEBT = "legacy_tech_debt"
    CLOUD_READY = "cloud_ready"
    MISSION_CRITICAL = "mission_critical"
    REDUNDANT_CAPABILITY = "redundant_capability"
    UNDERUTILIZED = "underutilized"
    WELL_OPTIMIZED = "well_optimized"
    SECURITY_CONCERN = "security_concern"


@dataclass
class ApplicationFeatures:
    """Normalized feature vector for an application."""
    app_id: str
    app_name: str

    # Core dimensions (0-1 normalized)
    business_value: float = 0.0
    technical_health: float = 0.0
    cost_efficiency: float = 0.0
    risk_score: float = 0.0
    user_adoption: float = 0.0
    integration_complexity: float = 0.0
    compliance_score: float = 0.0
    modernization_readiness: float = 0.0

    # Metadata
    category: str = ""
    vendor: str = ""
    annual_cost: float = 0.0
    user_count: int = 0

    def to_vector(self) -> List[float]:
        """Convert to feature vector for clustering."""
        return [
            self.business_value,
            self.technical_health,
            self.cost_efficiency,
            self.risk_score,
            self.user_adoption,
            self.integration_complexity,
            self.compliance_score,
            self.modernization_readiness
        ]

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "app_id": self.app_id,
            "app_name": self.app_name,
            "business_value": self.business_value,
            "technical_health": self.technical_health,
            "cost_efficiency": self.cost_efficiency,
            "risk_score": self.risk_score,
            "user_adoption": self.user_adoption,
            "integration_complexity": self.integration_complexity,
            "compliance_score": self.compliance_score,
            "modernization_readiness": self.modernization_readiness,
            "category": self.category,
            "vendor": self.vendor,
            "annual_cost": self.annual_cost,
            "user_count": self.user_count
        }


@dataclass
class Cluster:
    """A cluster of similar applications."""
    cluster_id: int
    name: str
    applications: List[ApplicationFeatures] = field(default_factory=list)
    centroid: List[float] = field(default_factory=list)
    characteristics: List[ClusterCharacteristic] = field(default_factory=list)

    # Cluster metrics
    cohesion_score: float = 0.0  # How tight the cluster is
    separation_score: float = 0.0  # How distinct from other clusters
    silhouette_score: float = 0.0

    # Insights
    consolidation_potential: float = 0.0
    estimated_savings: float = 0.0
    primary_action: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "cluster_id": self.cluster_id,
            "name": self.name,
            "application_count": len(self.applications),
            "applications": [app.to_dict() for app in self.applications],
            "centroid": self.centroid,
            "characteristics": [c.value for c in self.characteristics],
            "cohesion_score": self.cohesion_score,
            "separation_score": self.separation_score,
            "silhouette_score": self.silhouette_score,
            "consolidation_potential": self.consolidation_potential,
            "estimated_savings": self.estimated_savings,
            "primary_action": self.primary_action
        }


@dataclass
class ClusteringResult:
    """Complete clustering analysis result."""
    method: ClusteringMethod
    num_clusters: int
    clusters: List[Cluster] = field(default_factory=list)

    # Quality metrics
    overall_silhouette: float = 0.0
    inertia: float = 0.0
    davies_bouldin_index: float = 0.0

    # Optimal cluster analysis
    optimal_k: int = 0
    elbow_point: int = 0

    # Business insights
    total_consolidation_savings: float = 0.0
    consolidation_candidates: int = 0

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    feature_weights: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "method": self.method.value,
            "num_clusters": self.num_clusters,
            "clusters": [c.to_dict() for c in self.clusters],
            "overall_silhouette": self.overall_silhouette,
            "inertia": self.inertia,
            "davies_bouldin_index": self.davies_bouldin_index,
            "optimal_k": self.optimal_k,
            "elbow_point": self.elbow_point,
            "total_consolidation_savings": self.total_consolidation_savings,
            "consolidation_candidates": self.consolidation_candidates,
            "created_at": self.created_at.isoformat(),
            "feature_weights": self.feature_weights
        }


class MLClusteringEngine:
    """
    Machine Learning Clustering Engine for application portfolio analysis.
    Groups applications based on similarity to identify consolidation opportunities.
    """

    # Default feature weights
    DEFAULT_WEIGHTS = {
        "business_value": 1.0,
        "technical_health": 1.0,
        "cost_efficiency": 1.2,
        "risk_score": 0.8,
        "user_adoption": 0.9,
        "integration_complexity": 0.7,
        "compliance_score": 0.8,
        "modernization_readiness": 1.0
    }

    # Cluster naming patterns based on characteristics
    CLUSTER_NAMES = {
        ClusterCharacteristic.HIGH_COST_LOW_VALUE: "Cost Optimization Targets",
        ClusterCharacteristic.LEGACY_TECH_DEBT: "Technical Debt Carriers",
        ClusterCharacteristic.CLOUD_READY: "Cloud Migration Candidates",
        ClusterCharacteristic.MISSION_CRITICAL: "Core Business Systems",
        ClusterCharacteristic.REDUNDANT_CAPABILITY: "Consolidation Candidates",
        ClusterCharacteristic.UNDERUTILIZED: "Retirement Candidates",
        ClusterCharacteristic.WELL_OPTIMIZED: "Best Practice Examples",
        ClusterCharacteristic.SECURITY_CONCERN: "Security Priority Group"
    }

    def __init__(self, feature_weights: Optional[Dict[str, float]] = None):
        """Initialize clustering engine with optional custom weights."""
        self.weights = feature_weights or self.DEFAULT_WEIGHTS.copy()
        self._applications: List[ApplicationFeatures] = []
        self._result: Optional[ClusteringResult] = None

    def add_application(self, app: ApplicationFeatures) -> None:
        """Add an application to the clustering dataset."""
        self._applications.append(app)

    def add_applications(self, apps: List[ApplicationFeatures]) -> None:
        """Add multiple applications."""
        self._applications.extend(apps)

    def clear_applications(self) -> None:
        """Clear all applications."""
        self._applications = []
        self._result = None

    def _calculate_distance(
        self,
        v1: List[float],
        v2: List[float],
        metric: DistanceMetric = DistanceMetric.EUCLIDEAN
    ) -> float:
        """Calculate distance between two feature vectors."""
        if metric == DistanceMetric.EUCLIDEAN:
            return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))
        elif metric == DistanceMetric.MANHATTAN:
            return sum(abs(a - b) for a, b in zip(v1, v2))
        elif metric == DistanceMetric.COSINE:
            dot = sum(a * b for a, b in zip(v1, v2))
            norm1 = math.sqrt(sum(a ** 2 for a in v1))
            norm2 = math.sqrt(sum(b ** 2 for b in v2))
            if norm1 == 0 or norm2 == 0:
                return 1.0
            return 1 - (dot / (norm1 * norm2))
        return 0.0

    def _apply_weights(self, vector: List[float]) -> List[float]:
        """Apply feature weights to a vector."""
        weight_list = list(self.weights.values())
        return [v * w for v, w in zip(vector, weight_list)]

    def _calculate_centroid(self, apps: List[ApplicationFeatures]) -> List[float]:
        """Calculate centroid of a group of applications."""
        if not apps:
            return [0.0] * 8

        n = len(apps)
        vectors = [app.to_vector() for app in apps]
        centroid = []
        for i in range(len(vectors[0])):
            centroid.append(sum(v[i] for v in vectors) / n)
        return centroid

    def _kmeans_clustering(
        self,
        k: int,
        max_iterations: int = 100
    ) -> List[List[ApplicationFeatures]]:
        """Perform K-Means clustering."""
        if len(self._applications) < k:
            k = len(self._applications)

        # Initialize centroids randomly
        indices = random.sample(range(len(self._applications)), k)
        centroids = [self._apply_weights(self._applications[i].to_vector()) for i in indices]

        clusters: List[List[ApplicationFeatures]] = [[] for _ in range(k)]

        for iteration in range(max_iterations):
            # Clear clusters
            new_clusters: List[List[ApplicationFeatures]] = [[] for _ in range(k)]

            # Assign each application to nearest centroid
            for app in self._applications:
                weighted_vector = self._apply_weights(app.to_vector())
                distances = [
                    self._calculate_distance(weighted_vector, centroid)
                    for centroid in centroids
                ]
                nearest = distances.index(min(distances))
                new_clusters[nearest].append(app)

            # Handle empty clusters
            for i, cluster in enumerate(new_clusters):
                if not cluster:
                    # Assign random application to empty cluster
                    for j, other_cluster in enumerate(new_clusters):
                        if len(other_cluster) > 1:
                            new_clusters[i].append(other_cluster.pop())
                            break

            # Update centroids
            new_centroids = []
            for cluster in new_clusters:
                if cluster:
                    centroid = self._calculate_centroid(cluster)
                    new_centroids.append(self._apply_weights(centroid))
                else:
                    new_centroids.append(centroids[len(new_centroids)] if len(new_centroids) < len(centroids) else [0.0] * 8)

            # Check convergence
            if centroids == new_centroids:
                break

            centroids = new_centroids
            clusters = new_clusters

        return clusters

    def _calculate_silhouette(self, clusters: List[List[ApplicationFeatures]]) -> float:
        """Calculate overall silhouette score."""
        if len(clusters) < 2:
            return 0.0

        silhouettes = []

        for i, cluster in enumerate(clusters):
            for app in cluster:
                # a(i) = average distance to other points in same cluster
                if len(cluster) > 1:
                    a_i = sum(
                        self._calculate_distance(
                            self._apply_weights(app.to_vector()),
                            self._apply_weights(other.to_vector())
                        )
                        for other in cluster if other != app
                    ) / (len(cluster) - 1)
                else:
                    a_i = 0

                # b(i) = minimum average distance to points in other clusters
                b_i = float('inf')
                for j, other_cluster in enumerate(clusters):
                    if i != j and other_cluster:
                        avg_dist = sum(
                            self._calculate_distance(
                                self._apply_weights(app.to_vector()),
                                self._apply_weights(other.to_vector())
                            )
                            for other in other_cluster
                        ) / len(other_cluster)
                        b_i = min(b_i, avg_dist)

                if b_i == float('inf'):
                    b_i = 0

                # Silhouette coefficient
                if max(a_i, b_i) > 0:
                    s_i = (b_i - a_i) / max(a_i, b_i)
                else:
                    s_i = 0

                silhouettes.append(s_i)

        return sum(silhouettes) / len(silhouettes) if silhouettes else 0.0

    def _calculate_inertia(self, clusters: List[List[ApplicationFeatures]]) -> float:
        """Calculate within-cluster sum of squares (inertia)."""
        inertia = 0.0
        for cluster in clusters:
            if cluster:
                centroid = self._apply_weights(self._calculate_centroid(cluster))
                for app in cluster:
                    weighted_vector = self._apply_weights(app.to_vector())
                    inertia += self._calculate_distance(weighted_vector, centroid) ** 2
        return inertia

    def find_optimal_k(self, max_k: int = 10) -> Tuple[int, List[float]]:
        """Find optimal number of clusters using elbow method and silhouette analysis."""
        if len(self._applications) < 2:
            return 1, [0.0]

        max_k = min(max_k, len(self._applications))
        silhouette_scores = []
        inertias = []

        for k in range(2, max_k + 1):
            clusters = self._kmeans_clustering(k)
            silhouette = self._calculate_silhouette(clusters)
            inertia = self._calculate_inertia(clusters)
            silhouette_scores.append(silhouette)
            inertias.append(inertia)

        # Find elbow point (maximum curvature)
        if len(inertias) >= 3:
            # Calculate second derivative to find elbow
            second_derivatives = []
            for i in range(1, len(inertias) - 1):
                d2 = inertias[i-1] - 2*inertias[i] + inertias[i+1]
                second_derivatives.append(d2)

            elbow_idx = second_derivatives.index(max(second_derivatives)) + 2  # +2 because k starts at 2
        else:
            elbow_idx = 2

        # Find k with best silhouette score
        best_silhouette_k = silhouette_scores.index(max(silhouette_scores)) + 2

        # Combine both methods - prefer silhouette but consider elbow
        optimal_k = best_silhouette_k

        return optimal_k, silhouette_scores

    def _identify_characteristics(self, cluster: Cluster) -> List[ClusterCharacteristic]:
        """Identify characteristics of a cluster based on its centroid and members."""
        characteristics = []
        centroid = cluster.centroid

        if not centroid or len(centroid) < 8:
            return characteristics

        # Unpack centroid values
        biz_value, tech_health, cost_eff, risk, adoption, integration, compliance, modernization = centroid

        # High cost, low value
        if cost_eff < 0.4 and biz_value < 0.5:
            characteristics.append(ClusterCharacteristic.HIGH_COST_LOW_VALUE)

        # Legacy/tech debt
        if tech_health < 0.4 and modernization < 0.4:
            characteristics.append(ClusterCharacteristic.LEGACY_TECH_DEBT)

        # Cloud ready
        if modernization > 0.7 and tech_health > 0.6:
            characteristics.append(ClusterCharacteristic.CLOUD_READY)

        # Mission critical
        if biz_value > 0.8 and adoption > 0.7:
            characteristics.append(ClusterCharacteristic.MISSION_CRITICAL)

        # Underutilized
        if adoption < 0.3 and biz_value < 0.4:
            characteristics.append(ClusterCharacteristic.UNDERUTILIZED)

        # Well optimized
        if cost_eff > 0.7 and tech_health > 0.7 and biz_value > 0.6:
            characteristics.append(ClusterCharacteristic.WELL_OPTIMIZED)

        # Security concern
        if risk > 0.7 or compliance < 0.4:
            characteristics.append(ClusterCharacteristic.SECURITY_CONCERN)

        # Check for redundant capabilities (same category, similar features)
        categories = [app.category for app in cluster.applications]
        if len(categories) > 1:
            category_counts = defaultdict(int)
            for cat in categories:
                category_counts[cat] += 1
            # If most apps are in same category, potential redundancy
            max_count = max(category_counts.values())
            if max_count >= len(cluster.applications) * 0.6:
                characteristics.append(ClusterCharacteristic.REDUNDANT_CAPABILITY)

        return characteristics

    def _generate_cluster_name(self, characteristics: List[ClusterCharacteristic]) -> str:
        """Generate a descriptive name for a cluster based on its characteristics."""
        if not characteristics:
            return "General Applications"

        # Priority order for naming
        priority = [
            ClusterCharacteristic.MISSION_CRITICAL,
            ClusterCharacteristic.HIGH_COST_LOW_VALUE,
            ClusterCharacteristic.REDUNDANT_CAPABILITY,
            ClusterCharacteristic.LEGACY_TECH_DEBT,
            ClusterCharacteristic.CLOUD_READY,
            ClusterCharacteristic.SECURITY_CONCERN,
            ClusterCharacteristic.UNDERUTILIZED,
            ClusterCharacteristic.WELL_OPTIMIZED
        ]

        for char in priority:
            if char in characteristics:
                return self.CLUSTER_NAMES.get(char, "Application Cluster")

        return "Application Cluster"

    def _calculate_consolidation_potential(self, cluster: Cluster) -> Tuple[float, float, str]:
        """Calculate consolidation potential, estimated savings, and recommended action."""
        if len(cluster.applications) < 2:
            return 0.0, 0.0, "Maintain current state"

        chars = cluster.characteristics
        apps = cluster.applications
        total_cost = sum(app.annual_cost for app in apps)

        # Base consolidation potential on characteristics
        potential = 0.0
        action = "Review and optimize"

        if ClusterCharacteristic.REDUNDANT_CAPABILITY in chars:
            potential = 0.7
            action = "Consolidate to single platform"
        elif ClusterCharacteristic.HIGH_COST_LOW_VALUE in chars:
            potential = 0.6
            action = "Reduce costs or retire"
        elif ClusterCharacteristic.UNDERUTILIZED in chars:
            potential = 0.5
            action = "Consider retirement"
        elif ClusterCharacteristic.LEGACY_TECH_DEBT in chars:
            potential = 0.4
            action = "Modernize or replace"
        elif ClusterCharacteristic.CLOUD_READY in chars:
            potential = 0.3
            action = "Migrate to cloud"
        elif ClusterCharacteristic.MISSION_CRITICAL in chars:
            potential = 0.1
            action = "Protect and optimize"
        elif ClusterCharacteristic.WELL_OPTIMIZED in chars:
            potential = 0.05
            action = "Maintain as-is"

        # Estimate savings (percentage of total cost)
        savings = total_cost * potential * 0.4  # Conservative 40% of potential

        return potential, savings, action

    def cluster_applications(
        self,
        method: ClusteringMethod = ClusteringMethod.KMEANS,
        num_clusters: Optional[int] = None,
        auto_optimize: bool = True
    ) -> ClusteringResult:
        """
        Perform clustering analysis on loaded applications.

        Args:
            method: Clustering algorithm to use
            num_clusters: Number of clusters (if None, auto-determine)
            auto_optimize: Whether to find optimal cluster count

        Returns:
            ClusteringResult with clusters and insights
        """
        if len(self._applications) < 2:
            # Return single cluster with all apps
            cluster = Cluster(
                cluster_id=0,
                name="All Applications",
                applications=self._applications.copy(),
                centroid=self._calculate_centroid(self._applications)
            )
            return ClusteringResult(
                method=method,
                num_clusters=1,
                clusters=[cluster],
                optimal_k=1
            )

        # Determine number of clusters
        if num_clusters is None or auto_optimize:
            optimal_k, silhouette_scores = self.find_optimal_k()
            k = num_clusters or optimal_k
        else:
            k = num_clusters
            silhouette_scores = []

        # Perform clustering
        if method == ClusteringMethod.KMEANS:
            raw_clusters = self._kmeans_clustering(k)
        else:
            # Default to K-Means for now
            raw_clusters = self._kmeans_clustering(k)

        # Build cluster objects
        clusters = []
        total_savings = 0.0
        consolidation_count = 0

        for i, apps in enumerate(raw_clusters):
            if not apps:
                continue

            centroid = self._calculate_centroid(apps)
            cluster = Cluster(
                cluster_id=i,
                name=f"Cluster {i+1}",
                applications=apps,
                centroid=centroid
            )

            # Identify characteristics
            cluster.characteristics = self._identify_characteristics(cluster)
            cluster.name = self._generate_cluster_name(cluster.characteristics)

            # Calculate metrics
            cluster.cohesion_score = 1.0 / (1.0 + self._calculate_inertia([apps]))

            # Calculate consolidation potential
            potential, savings, action = self._calculate_consolidation_potential(cluster)
            cluster.consolidation_potential = potential
            cluster.estimated_savings = savings
            cluster.primary_action = action

            total_savings += savings
            if potential > 0.3:
                consolidation_count += len(apps)

            clusters.append(cluster)

        # Calculate overall metrics
        overall_silhouette = self._calculate_silhouette(raw_clusters)
        inertia = self._calculate_inertia(raw_clusters)

        # Build result
        result = ClusteringResult(
            method=method,
            num_clusters=len(clusters),
            clusters=clusters,
            overall_silhouette=overall_silhouette,
            inertia=inertia,
            optimal_k=k,
            total_consolidation_savings=total_savings,
            consolidation_candidates=consolidation_count,
            feature_weights=self.weights.copy()
        )

        self._result = result
        return result

    def get_consolidation_opportunities(self) -> List[Dict]:
        """Get list of consolidation opportunities from clustering results."""
        if not self._result:
            return []

        opportunities = []
        for cluster in self._result.clusters:
            if cluster.consolidation_potential >= 0.3:
                opportunities.append({
                    "cluster_id": cluster.cluster_id,
                    "cluster_name": cluster.name,
                    "application_count": len(cluster.applications),
                    "applications": [app.app_name for app in cluster.applications],
                    "consolidation_potential": cluster.consolidation_potential,
                    "estimated_savings": cluster.estimated_savings,
                    "recommended_action": cluster.primary_action,
                    "characteristics": [c.value for c in cluster.characteristics]
                })

        # Sort by potential savings
        opportunities.sort(key=lambda x: x["estimated_savings"], reverse=True)
        return opportunities

    def get_cluster_comparison(self) -> List[Dict]:
        """Get comparison metrics across all clusters."""
        if not self._result:
            return []

        comparisons = []
        for cluster in self._result.clusters:
            apps = cluster.applications
            comparisons.append({
                "cluster_id": cluster.cluster_id,
                "cluster_name": cluster.name,
                "app_count": len(apps),
                "total_cost": sum(app.annual_cost for app in apps),
                "total_users": sum(app.user_count for app in apps),
                "avg_business_value": sum(app.business_value for app in apps) / len(apps) if apps else 0,
                "avg_technical_health": sum(app.technical_health for app in apps) / len(apps) if apps else 0,
                "avg_cost_efficiency": sum(app.cost_efficiency for app in apps) / len(apps) if apps else 0,
                "characteristics": [c.value for c in cluster.characteristics]
            })

        return comparisons


def create_clustering_engine(weights: Optional[Dict[str, float]] = None) -> MLClusteringEngine:
    """Factory function to create a clustering engine."""
    return MLClusteringEngine(feature_weights=weights)


def create_demo_applications(count: int = 30) -> List[ApplicationFeatures]:
    """Create demo application data for testing."""
    categories = [
        "CRM", "ERP", "HRM", "Finance", "Marketing",
        "Analytics", "Communication", "Collaboration",
        "Security", "DevOps", "Database", "Reporting"
    ]

    vendors = [
        "Salesforce", "Microsoft", "SAP", "Oracle", "Workday",
        "ServiceNow", "Adobe", "Google", "AWS", "IBM",
        "Custom Built", "Open Source"
    ]

    # Create different application profiles
    profiles = [
        # High value, healthy
        {"biz": (0.7, 1.0), "tech": (0.7, 1.0), "cost": (0.6, 0.9), "risk": (0.1, 0.3), "modern": (0.7, 1.0)},
        # Legacy, technical debt
        {"biz": (0.4, 0.7), "tech": (0.2, 0.5), "cost": (0.3, 0.5), "risk": (0.5, 0.8), "modern": (0.1, 0.4)},
        # Underutilized
        {"biz": (0.1, 0.4), "tech": (0.4, 0.7), "cost": (0.2, 0.4), "risk": (0.3, 0.5), "modern": (0.4, 0.7)},
        # High cost, low value
        {"biz": (0.2, 0.5), "tech": (0.4, 0.7), "cost": (0.1, 0.3), "risk": (0.4, 0.6), "modern": (0.3, 0.6)},
        # Cloud ready
        {"biz": (0.5, 0.8), "tech": (0.7, 0.9), "cost": (0.5, 0.8), "risk": (0.2, 0.4), "modern": (0.8, 1.0)},
    ]

    applications = []
    for i in range(count):
        profile = random.choice(profiles)
        category = random.choice(categories)
        vendor = random.choice(vendors)

        app = ApplicationFeatures(
            app_id=f"APP-{i+1:04d}",
            app_name=f"{category} System {i+1}",
            business_value=random.uniform(*profile["biz"]),
            technical_health=random.uniform(*profile["tech"]),
            cost_efficiency=random.uniform(*profile["cost"]),
            risk_score=random.uniform(*profile["risk"]),
            user_adoption=random.uniform(0.2, 0.9),
            integration_complexity=random.uniform(0.2, 0.8),
            compliance_score=random.uniform(0.5, 1.0),
            modernization_readiness=random.uniform(*profile["modern"]),
            category=category,
            vendor=vendor,
            annual_cost=random.uniform(10000, 500000),
            user_count=random.randint(10, 5000)
        )
        applications.append(app)

    return applications

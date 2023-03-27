from dagster._config.structured_config.resource_verification import VerificationResult
from dagster._core.definitions.selector import ResourceSelector
from dagster._core.errors import DagsterLaunchFailedError
from dagster._core.instance import DagsterInstance
from dagster._core.workspace.context import WorkspaceRequestContext
from git import TYPE_CHECKING

if TYPE_CHECKING:
    from dagster_graphql.schema.util import ResolveInfo


def resource_verification(
    graphene_info: "ResolveInfo", resource_selector: ResourceSelector
) -> VerificationResult:
    instance: DagsterInstance = graphene_info.context.instance

    context: WorkspaceRequestContext = graphene_info.context

    location = context.get_code_location(resource_selector.location_name)
    repository = location.get_repository(resource_selector.repository_name)

    res = location.launch_resource_verification(
        origin=repository.get_external_origin(),
        instance_ref=instance.get_ref(),
        resource_name=resource_selector.resource_name,
    )
    if res.serializable_error_info:
        raise (DagsterLaunchFailedError(res.serializable_error_info))
    return res.response

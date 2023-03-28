# isort: skip_file


from typing import Dict, List


class Engine:
    def execute(self, query: str):
        ...


def get_engine(connection_url: str) -> Engine:
    return Engine()


def basic_resource_config() -> None:
    # start_basic_resource_config

    from dagster import op, ConfigurableResource

    class MyDatabaseResource(ConfigurableResource):
        connection_url: str

        def query(self, query: str):
            return get_engine(self.connection_url).execute(query)

    # end_basic_resource_config


def execute_with_config() -> None:
    # start_basic_op_config

    from dagster import op, Config

    class MyOpConfig(Config):
        person_name: str

    @op
    def print_greeting(config: MyOpConfig):
        print(f"hello {config.person_name}")  # noqa: T201

    # end_basic_op_config

    # start_basic_asset_config

    from dagster import asset, Config

    class MyAssetConfig(Config):
        person_name: str

    @asset
    def greeting(config: MyAssetConfig) -> str:
        return f"hello {config.person_name}"

    # end_basic_asset_config

    # start_execute_with_config
    from dagster import job, materialize, op, RunConfig

    @job
    def greeting_job():
        print_greeting()

    job_result = greeting_job.execute_in_process(
        run_config=RunConfig({"print_greeting": MyOpConfig(person_name="Alice")})  # type: ignore
    )

    asset_result = materialize(
        [greeting],
        run_config=RunConfig({"greeting": MyAssetConfig(person_name="Alice")}),
    )

    # end_execute_with_config

    # start_execute_with_config_envvar
    from dagster import job, materialize, op, RunConfig, EnvVar

    job_result = greeting_job.execute_in_process(
        run_config=RunConfig({"print_greeting": MyOpConfig(person_name=EnvVar("PERSON_NAME"))})  # type: ignore
    )

    asset_result = materialize(
        [greeting],
        run_config=RunConfig(
            {"greeting": MyAssetConfig(person_name=EnvVar("PERSON_NAME"))}
        ),
    )

    # end_execute_with_config_envvar


def basic_data_structures_config() -> None:
    # start_basic_data_structures_config
    from dagster import Config, materialize, asset, RunConfig
    from typing import List, Dict

    class MyDataStructuresConfig(Config):
        user_names: List[str]
        user_scores: Dict[str, int]

    @asset
    def scoreboard(config: MyDataStructuresConfig):
        ...

    result = materialize(
        [scoreboard],
        run_config=RunConfig(
            {
                "scoreboard": MyDataStructuresConfig(
                    user_names=["Alice", "Bob"],
                    user_scores={"Alice": 10, "Bob": 20},
                )
            }
        ),
    )

    # end_basic_data_structures_config


def nested_schema_config() -> None:
    # start_nested_schema_config
    from dagster import asset, materialize, Config, RunConfig
    from typing import Dict

    class UserData(Config):
        age: int
        email: str
        profile_picture_url: str

    class MyNestedConfig(Config):
        user_data: Dict[str, UserData]

    @asset
    def average_age(config: MyNestedConfig):
        ...

    result = materialize(
        [average_age],
        run_config=RunConfig(
            {
                "average_age": MyNestedConfig(
                    user_data={
                        "Alice": UserData(age=10, email="alice@gmail.com", profile_picture_url=...),  # type: ignore
                        "Bob": UserData(age=20, email="bob@gmail.com", profile_picture_url=...),  # type: ignore
                    }
                )
            }
        ),
    )

    # end_nested_schema_config


def union_schema_config() -> None:
    # start_union_schema_config

    from dagster import asset, materialize, Config, RunConfig
    from pydantic import Field
    from typing import Union
    from typing_extensions import Literal

    class Cat(Config):
        pet_type: Literal["cat"] = "cat"
        meows: int

    class Dog(Config):
        pet_type: Literal["dog"] = "dog"
        barks: float

    class ConfigWithUnion(Config):
        # Here, the ellipses `...` indicates that the field is required and has no default value.
        pet: Union[Cat, Dog] = Field(..., discriminator="pet_type")

    @asset
    def pet_stats(config: ConfigWithUnion):
        if isinstance(config.pet, Cat):
            return f"Cat meows {config.pet.meows} times"
        else:
            return f"Dog barks {config.pet.barks} times"

    result = materialize(
        [pet_stats],
        run_config=RunConfig(
            {
                "pet_stats": ConfigWithUnion(
                    pet=Cat(meows=10),
                )
            }
        ),
    )
    # end_union_schema_config


def metadata_config() -> None:
    #  start_metadata_config
    from dagster import Config
    from pydantic import Field

    class MyMetadataConfig(Config):
        # Here, the ellipses `...` indicates that the field is required and has no default value.
        person_name: str = Field(..., description="The name of the person to greet")
        age: int = Field(
            ..., gt=0, lt=100, description="The age of the person to greet"
        )

    # errors!
    MyMetadataConfig(person_name="Alice", age=200)

    # end_metadata_config


def optional_config() -> None:
    # start_optional_config

    from typing import Optional
    from dagster import asset, Config, materialize, RunConfig

    class MyAssetConfig(Config):
        person_name: Optional[str] = None
        greeting_phrase: str = "hello"

    @asset
    def greeting(config: MyAssetConfig) -> str:
        if config.person_name:
            return f"{config.greeting_phrase} {config.person_name}"
        else:
            return config.greeting_phrase

    asset_result = materialize(
        [greeting],
        run_config=RunConfig({"greeting": MyAssetConfig()}),
    )

    # end_optional_config


def execute_with_bad_config() -> None:
    from dagster import op, job, materialize, Config, RunConfig

    class MyOpConfig(Config):
        person_name: str

    @op
    def print_greeting(config: MyOpConfig):
        print(f"hello {config.person_name}")  # noqa: T201

    from dagster import asset, Config

    class MyAssetConfig(Config):
        person_name: str

    @asset
    def greeting(config: MyAssetConfig) -> str:
        return f"hello {config.person_name}"

    # start_execute_with_bad_config

    @job
    def greeting_job():
        print_greeting()

    op_result = greeting_job.execute_in_process(
        run_config=RunConfig({"print_greeting": MyOpConfig(nonexistent_config_param=1)}),  # type: ignore
    )

    asset_result = materialize(
        [greeting],
        run_config=RunConfig({"greeting": MyAssetConfig(nonexistent_config_param=1)}),  # type: ignore
    )

    # end_execute_with_bad_config


def enum_schema_config() -> None:
    # start_enum_schema_config

    from dagster import Config, RunConfig, op, job
    from enum import Enum

    class UserPermissions(Enum):
        GUEST = "guest"
        MEMBER = "member"
        ADMIN = "admin"

    class ProcessUsersConfig(Config):
        users_list: Dict[str, UserPermissions]

    @op
    def process_users(config: ProcessUsersConfig):
        for user, permission in config.users_list.items():
            if permission == UserPermissions.ADMIN:
                print(f"{user} is an admin")

    @job
    def process_users_job():
        process_users()

    op_result = process_users_job.execute_in_process(
        run_config=RunConfig(
            {
                "process_users": ProcessUsersConfig(
                    users_list={
                        "Bob": UserPermissions.GUEST,
                        "Alice": UserPermissions.ADMIN,
                    }
                )
            }
        ),  # type: ignore
    )
    # end_enum_schema_config


def validated_schema_config() -> None:
    # start_validated_schema_config

    from dagster import Config, RunConfig, op, job
    from pydantic import validator

    class UserConfig(Config):
        name: str
        username: str

        @validator("name")
        def name_must_contain_space(cls, v):
            if " " not in v:
                raise ValueError("must contain a space")
            return v.title()

        @validator("username")
        def username_alphanumeric(cls, v):
            assert v.isalnum(), "must be alphanumeric"
            return v

    executed = {}

    @op
    def greet_user(config: UserConfig) -> None:
        print(f"Hello {config.name}!")  # noqa: T201
        executed["greet_user"] = True

    @job
    def greet_user_job() -> None:
        greet_user()

    # Input is valid, so this will work
    op_result = greet_user_job.execute_in_process(
        run_config=RunConfig(
            {"greet_user": UserConfig(name="Alice Smith", username="alice123")}
        ),  # type: ignore
    )

    # Name has no space, so this will fail
    op_result = greet_user_job.execute_in_process(
        run_config=RunConfig(
            {"greet_user": UserConfig(name="John", username="johndoe44")}
        ),  # type: ignore
    )

    # end_validated_schema_config

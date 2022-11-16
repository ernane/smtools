from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=["settings.yaml"],
    core_loaders=["YAML"],
    root_path="smtools/ext/settings",
    includes=["../manifests/*.yaml"],
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.

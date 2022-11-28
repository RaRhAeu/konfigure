# Konfigure

*Dynamic configuration and schema management service*


## About

`Konfigure` is a dynamic configuration service, providing RESTful HTTP API,
for other services to consume. It's not bound to any tech stack, or language.

## Features:

- `Namespaces` - separation of configurations per namespace (eg. dev/stage/prod)
- `Secrets` - Store sensitive information, with encryption-at-rest.
- `ConfigDefinition` - define custom configuration types via `yaml`,
    just like you would define a kubernetes CRD.
- Dynamic docs (swagger) - documentation is regenerated each time a new `ConfigDefinition` is created, allowing customizing validation and automatic client generation


## Example

```yaml
apiVersion: configdefinitions.io/v1
kind: ConfigDefinition
metadata:
  name: url-configuration
spec:
  group: urls
  names:
    kind: Url
    plural: urls
  versions:
    - name: v1
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              required: [url]
              properties:
                url:
                  type: string
```
async def create_custom_aliases(es, params):
    actions = []
    for component in range(1, 10 + 1):
        for type_ in range(1, 10 + 1):
            for tag in range(1, 10 + 1):
                for year in range(1, 10 + 1):
                    actions.append(
                        {
                            "add": {
                                "index": "index",
                                "alias": f"alias-component{component}-type{type_}-tag{tag}-year{year}",
                            }
                        }
                    )
    await es.indices.update_aliases({"actions": actions})


def register(registry):
    registry.register_runner("create-custom-aliases", create_custom_aliases, async_runner=True)

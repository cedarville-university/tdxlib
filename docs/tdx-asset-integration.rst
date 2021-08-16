TDX Asset Integration
=====================

This class contains all the methods that work with the TDX Asset API endpoints.

This class inherits the base TDX integration class.

Searching for Assets
--------------------

Special Characters
__________________

Using the method ``search_assets()`` exposes a few undocumented features in TDX's Web API. The primary one is some limited support for Regular Expressions in the SearchText parameter. This can be confusing because you may occasionally specify a Regex special character without realizing it.

For instance, you may use the following:

.. code-block:: python

    my_asset_integration_object.search_assets('K-')

This would be a pretty broad search anyway, but because of the way the TDX API interprets it, it actually includes all assets that have a "K" in their name or Serial number, or a number of other fields.

If to search for assets whose names or serial numbers begin with "K-", use the following:

.. code-block:: python

    my_asset_integration_object.search_assets('^K-')

This search returns more what you would expect.

Normal searches with only alphanumerical characters work as expected.

Searching with Attributes
_________________________

The following may be useful if you need to filter by a specific product type:

.. code-block:: python

    prodmod = my_asset_integration_object.get_all_product_models()

Then, set up a list for the models you actually want:

.. code-block:: python

    models = []

Then run a quick loop, appending to the list:

.. code-block:: python

    for mod in prodmod:
        if mod['ProductTypeName'] == "Desktop" or mod['ProductTypeName'] == "Laptop":
            models.append(mod['ID'])

Then use this info in a filter in ``search_assets()``

.. code-block:: python

    criteria = {'ProductModelIDs': models}
    assets = my_asset_integration_object.search_assets(criteria, max_results=1000)

Searching with Custom Attributes
________________________________

If you'd like to search for assets that have a specific value for a custom attribute, you'll need to do something similar:

.. code-block:: python

    ca = t.build_asset_custom_attribute_value("My CA Name", "My Value Name")
    criteria = {'CustomAttributes': [ca]}
    assets = my_asset_integration_object.search_assets(criteria, max_results=1000)

This will find all assets with the value "My Value Name" for the Custom Attribute "My CA Name".

For more information check out the documentation on the `AssetSearch object in TDX's API docs <https://api.teamdynamix.com/TDWebApi/Home/type/TeamDynamix.Api.Assets.AssetSearch>`_

Custom Attributes
-----------------

Custom Attributes are so useful in TeamDynamix and so difficult to understand in the API that it's worth a section in the documentation dealing directly with them.

The simplest use case is to set a custom attribute to a certain value on an asset.

1. Set up your TDX Integration:

.. code-block:: python

    import tdxlib
    t = tdxlib.tdxassetintegration.TdxAssetIntegration()

2. Set up your dict of updated values with CA and value that you would like to set. This command retrieves the CA ID and the ID of the choice you selected (if a choice variable) and formats it correctly for ingestion by TDX. If it is a non-choice field, it will simply include the second attribute as the value of the CA.

.. code-block:: python

    update = {'Attributes': [t.build_asset_custom_attribute_value("My CA Name", "My Value Name")]}

3. To add more attributes:

.. code-block:: python

    update['Attributes'].append(t.build_asset_custom_attribute_value("My Other CA Name", "My Other Value Name"))

4. Get the assets you want to update:

.. code-block:: python

    assets = t.search_assets("KIOSK")

5. Update the assets:

.. code-block:: python

    updated_assets = t.update_assets(assets, update)

Class & Methods
---------------

.. autoclass:: tdxlib.tdx_asset_integration.TDXAssetIntegration
    :members:


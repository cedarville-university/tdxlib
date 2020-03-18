TDX Asset Integration
=====================

This class contains all the methods that work with the TDX Asset API endpoints.

This class inherits the base TDX integration class.

Custom Attributes
-----------------

Custom Attributes are so useful in TeamDynamix and so difficult to understand in the API that it's worth a section in the documentation dealing directly with them.

The simplest use case is to set a custom attribute to a certain value on an asset.

1. Set up your TDX Integration:

    ``import tdxlib``

    ``t = tdxlib.tdxassetintegration.TdxAssetIntegration()``

2. Set up your dict of updated values with CA and value that you would like to set. This command retrieves the CA ID and the ID of the choice you selected (if a choice variable) and formats it correctly for ingestion by TDX. If it is a non-choice field, it will simply include the second attribute as the value of the CA.

    ``update = {'Attributes': [t.build_asset_custom_attribute_value("My CA Name", "My Value Name")]}``

3. To add more attributes:

    ``update['Attributes'].append(t.build_asset_custom_attribute_value("My Other CA Name", "My Other Value Name"))``

4. Get the assets you want to update:

    ``assets = t.search_assets("KIOSK")``

5. Update the assets:

    ``updated_assets = t.update_assets(assets, update)``


Class & Methods
---------------

.. autoclass:: tdxlib.tdx_asset_integration.TDXAssetIntegration
    :members:


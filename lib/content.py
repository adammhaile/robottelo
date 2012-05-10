#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ts=4 sw=4 expandtab ai

from base import Base
from common import *
from locators import *

from robot.api import logger
from robot.utils import asserts

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException


class content(object):
    """
    Performs actions related creating, adding, editing and deleting
    content to an existing organization.
    """

    __version__ = '0.1'


    def __init__(self):
        self.base = Base()


    def go_to_content_tab(self):
        """
        Takes user to the Content Management tab in the ui.
        """

        return select_tab(self.base.driver, HEADER_CONTENT_MANAGEMENT)


    def select_content_provider(self, content_provider_type):
        """
        Selects the content provider type
        """

        # Hover over the Content Provider link
        content_provider_link = wait_until_element(self.base.driver, SUB_HEADER_CONTENT_PROVIDER, By.XPATH)
        try:
            hover = ActionChains(self.base.driver).move_to_element(content_provider_link)
            asserts.fail_if_none(hover, "Failed to move the mouse over the Contant Providers link.")
            hover.perform()
            provider = wait_until_element(self.base.driver, PROVIDER % content_provider_type, By.XPATH)
            asserts.fail_if_none(provider, "Could not locate the content provider type.")
            provider.click()
        except WebDriverException, e:
            logger.debug("Cannot perform native interaction! See https://groups.google.com/group/webdriver/browse_thread/thread/f7130084c623f337/568fe9e85b6fd658?lnk=raot&pli=1 for more information. Error: %s" % str(e))
            # TODO: Find a better way to handle this if bug above is not fixed soon!!!
            if "custom" in content_provider_type:
                url = self.base.driver.current_url
            elif "redhat" in content_provider_type:
                url = "%s/redhat_provider" % self.base.driver.current_url
            elif "filters" in content_provider_type:
                url = "%s/filters" % self.base.base_url
            else:
                url = "%s/gpg_keys" % self.base.base_url

            self.base.driver.get(url)
        except NoSuchElementException, e:
            asserts.fail("Could not select the '%s' content type" % content_provider_type)


    def _get_provider_by_name(self, name):
        """
        Returns the Provider and ID that matches the name provided.
        """

        _prod = None
        _id = None

        providers = self.base.driver.find_elements_by_xpath(PROVIDERS)

        for provider in providers:
            we = provider.find_element_by_xpath(PROVIDER_BY_TITLE % name)
            if name in we.text:
                _prod = we
                # provider id is derived from: id=provider_39
                _id = provider.get_attribute('id').split('_')[-1]
                break

        return (_prod, _id)


    def _get_product_by_name(self, name):
        """
        Returns the Product and ID that matches the name provided.
        """

        _prod = None
        _id = None

        products = self.base.driver.find_elements_by_xpath(PRODUCTS)

        for product in products:
            we = product.find_element_by_xpath(PRODUCT)
            if name in we.text:
                _prod = we
                we_id = product.find_element_by_xpath(PRODUCT_ID)
                # product id is derived from: data-url=/cfse/providers/39/products/13/edit
                _id = we_id.get_attribute('data-url').split('/')[5]
                break

        return (_prod, _id)


    def add_custom_provider(self, provider_name):
        """
        Adds a custom provider.
        """

        # Select Contents tab
        asserts.assert_true(self.go_to_content_tab(), "Could not access the Content Management tab.")

        # Select custom provider type
        self.select_content_provider(CUSTOM_PROVIDERS)

        (provider, provider_id) = self._get_provider_by_name(provider_name)
        asserts.fail_unless_none(provider, "Found a provider with that name already.")

        new_provider_link = wait_until_element(self.base.driver, "//a[@id='new']", By.XPATH)
        asserts.fail_if_none(new_provider_link, "Failed to locate the New Provider link.")
        new_provider_link.click()

        provider_name = wait_until_element(self.base.driver, PROVIDER_NAME_FIELD, By.XPATH)
        asserts.fail_if_none(provider_name, "Failed to locate the provider Name field.")
        provider_name.send_keys(provider_name)

        provider_description = wait_until_element(self.base.driver, PROVIDER_DESCRIPTION_FIELD, By.XPATH)
        asserts.fail_if_none(provider_description, "Failed to locate the provider Description field.")
        provider_description.send_keys("Automatically created by Robottelo.")

        provider_save = wait_until_element(self.base.driver, PROVIDER_SAVE_BUTTON, By.XPATH)
        asserts.fail_if_none(provider_save, "Could not locate the Save button.")
        provider_save.click()

        (provider, provider_id) = self._get_provider_by_name(provider_name)
        asserts.fail_if_none(provider, "Could not locate the '%s' provider." % provider_name)


    def delete_custom_provider(self, provider_name):
        """
        Deletes the specified provider from an organization.
        """

        # Select Contents tab
        asserts.assert_true(self.go_to_content_tab(), "Could not access the Content Management tab.")

        # Select custom provider type
        self.select_content_provider(CUSTOM_PROVIDERS)

        (provider, provider_id) = self._get_provider_by_name(provider_name)
        asserts.fail_if_none(provider, "Could not locate the '%s' provider." % provider_name)
        provider.click()

        remove_link = wait_until_element(self.base.driver, PROVIDER_REMOVE_LINK % provider_id, By.XPATH)
        remove_link.click()

        # Find the Yes button
        yes_button = wait_until_element(self.base.driver, YES_BUTTON, By.XPATH)
        asserts.fail_if_none(yes_button, "Could not find the Yes button to remove role.")
        yes_button.click()

        # Visit providers again
        self.select_content_provider(CUSTOM_PROVIDERS)
        (provider, provider_id) = self._get_provider_by_name(provider_name)
        asserts.fail_unless_none(provider, "Found a provider with that name already.")


    def add_product_to_provider(self, provider_name, product_name):
        """
        Adds a product to an existing provider.
        """

        # Select Contents tab
        asserts.assert_true(self.go_to_content_tab(), "Could not access the Content Management tab.")

        # Select custom provider type
        self.select_content_provider(CUSTOM_PROVIDERS)

        (provider, provider_id) = self._get_provider_by_name(provider_name)
        asserts.fail_if_none(provider, "Could not locate the '%s' provider." % provider_name)
        provider.click()

        (product, product_id) = self._get_product_by_name(product_name)
        asserts.fail_unless_none(product, "Found a provider with that name already.")

        add_product_button = wait_until_element(self.base.driver, NEW_PRODUCT_BUTTON, By.XPATH)
        asserts.fail_if_none(add_product_button, "Could not locate the Add Product button.")
        add_product_button.click()

        product_name_field = wait_until_element(self.base.driver, PRODUCT_NAME_FIELD, By.XPATH)
        product_name_field.send_keys(product_name)

        product_description_field = wait_until_element(self.base.driver, PRODUCT_DESCRIPTION_FIELD, By.XPATH)
        product_description_field.send_keys("Automatically created by Robottelo.")

        create_button = wait_until_element(self.base.driver, PRODUCT_SAVE_BUTTON, By.XPATH)
        create_button.click()

        (product, product_id) = self._get_product_by_name(product_name)
        asserts.fail_if_none(product, "Could not locate the '%s' product." % product_name)


    def delete_product_from_provider(self, provider_name, product_name):
        """
        Deletes the specified product from a provider.
        """

        # Select Contents tab
        asserts.assert_true(self.go_to_content_tab(), "Could not access the Content Management tab.")

        # Select custom provider type
        self.select_content_provider(CUSTOM_PROVIDERS)

        (provider, provider_id) = self._get_provider_by_name(provider_name)
        asserts.fail_if_none(provider, "Could not locate the '%s' provider." % provider_name)
        provider.click()

        (product, product_id) = self._get_product_by_name(product_name)
        asserts.fail_if_none(product, "Could not locate the '%s' product." % product_name)
        product.click()

        remove_link = wait_until_element(self.base.driver, PRODUCT_REMOVE_LINK % provider_id, By.XPATH)
        asserts.fail_if_none(remove_link, "Failed to locate the Remove Product link.")
        remove_link.click()

        # Find the Yes button
        yes_button = wait_until_element(self.base.driver, YES_BUTTON, By.XPATH)
        asserts.fail_if_none(yes_button, "Could not find the Yes button to remove role.")
        yes_button.click()

        (product, product_id) = self._get_product_by_name(product_name)
        asserts.fail_unless_none(product, "Found a provider with that name already.")


    def red_hat_provider(self, manifest, force=True):
        """
        Uploads a Red Hat manifest file.
        """

        # Select Contents tab
        asserts.assert_true(self.go_to_content_tab(), "Could not access the Content Management tab.")

        # Select Red Hat content type
        self.select_content_provider(REDHAT_PROVIDERS)

        manifest_file = get_manifest_file(manifest)

        # Check for the manifest field
        manifest_field = wait_until_element(self.base.driver, MANIFEST_FILE_FIELD, By.XPATH)
        asserts.fail_if_none(manifest_field, "Could not locate the manifest field.")
        # This is the path to the manifest file
        logger.debug(manifest_file)
        manifest_field.send_keys(manifest_file)

        # Force it?
        if force:
            # Locate the Force checkbox
            force_checkbox = wait_until_element(self.base.driver, MANIFEST_FORCE_CHECKBOX, By.XPATH)
            asserts.fail_if_none(force_checkbox, "Could not locate the Force checkbox.")
            force_checkbox.click()

        # Find the import link
        submit_button = wait_until_element(self.base.driver, MANIFEST_SAVE_BUTTON, By.XPATH)
        submit_button.click()

        # TODO: Find a way to improve validation. count("//table[@id='redhatSubscriptionTable']/tbody/tr")?
        subscriptions = wait_until_element(self.base.driver, SUBSCRIPTIONS, By.XPATH)
        asserts.fail_if_none(subscriptions, "Could not find a subscription.")


    def enable_repository(self, product, version, arch, component):
        """
        Enables the repository specified.
        """

        # Select Contents tab
        asserts.assert_true(self.go_to_content_tab(), "Could not access the Content Management tab.")

        # Select Red Hat content type
        self.select_content_provider(REDHAT_PROVIDERS)

        # Locate the Enable Repo tab
        enable_repos_tab = wait_until_element(self.base.driver, ENABLE_REPOS_TAB, By.XPATH)
        asserts.fail_if_none(enable_repos_tab, "Could not locate the Enable Repo tab.")
        enable_repos_tab.click()

        # Select the product
        product_span= wait_until_element(self.base.driver, RHEL_PRODUCT % product, By.XPATH)
        asserts.fail_if_none(product_span, "Could not locate the '%s' product." % product)
        product_node = wait_until_element(self.base.driver, RHEL_PRODUCT_ID % product, By.XPATH)
        product_id = product_node.get_attribute("id")
        product_span.click()

        # Select the version
        version_span = wait_until_element(self.base.driver, RHEL_PRODUCT_VERSION % (product_id, version), By.XPATH)
        asserts.fail_if_none(version_span, "Could not locate the '%s' version." % version)
        version_span.click()

        # Select the arch
        arch_span = wait_until_element(self.base.driver, RHEL_PRODUCT_ARCH % (product_id, version, arch), By.XPATH)
        asserts.fail_if_none(arch_span, "Could not locate the '%s' arch." % arch)
        arch_span.click()

        # Select the component
        repo = wait_until_element(self.base.driver, RHEL_PRODUCT_REPO % (product_id, version, arch, component), By.XPATH)
        asserts.fail_if_none(repo, "Could not locate the repository '%s'." % component)
        repo.click()
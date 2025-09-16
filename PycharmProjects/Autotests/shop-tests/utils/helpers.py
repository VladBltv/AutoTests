from befree.api_model.catalog.db_queries.queries import QueriesCatalog
import os
import datetime
import random
import secrets
import string


class Helpers:
    def is_sorted(self, l, direction="asc"):
        """Check if the list is sorted in ascending or descending order

        Args:
            l (list): The list to check.
            direction (str): The direction to check.

        Returns:
            bool: True if the list is sorted in ascending or descending order, False otherwise.
        """
        if direction == "asc":
            return all(a <= b for a, b in zip(l, l[1:]))
        elif direction == "desc":
            return all(a >= b for a, b in zip(l, l[1:]))

    def is_exists_in_data_list(self, ref_key, ref_value, data):
        """Check if the value exists in the list of dictionaries

        Args:
            ref_key (str): The key to search for.
            ref_value (int): The value to search for.
            data (list): The list of dictionaries to search in.

        Returns:
            bool: True if the value exists in the list of dictionaries, False otherwise.
        """
        return any(
            list(
                map(
                    lambda x: x[ref_key] == ref_value,
                    data,
                )
            )
        )

    def count_value_key_in_list(self, iterable, key, value):
        """Count the number of times the value appears in the list of dictionaries

        Args:
            iterable (list): The list of dictionaries to search in.
            key (str): The key to search for.
            value (int): The value to search for.

        Returns:
            int: The number of times the value appears in the list of dictionaries.
        """
        count = 0
        for index, dict_ in enumerate(iterable):
            if key in dict_ and dict_[key] == value:
                count += 1

        return count

    def index_value_key_in_list(self, iterable, key, value):
        """Find the index of the value in the list of dictionaries

        Args:
            iterable (list): The list of dictionaries to search in.
            key (str): The key to search for.
            value (int): The value to search for.

        Returns:
            int: The index of the value in the list of dictionaries.
        """
        for index, dict_ in enumerate(iterable):
            if key in dict_ and dict_[key] == value:
                return index

    def find_by_qty(self, iterable, key, value):
        """Find the item in the list of dictionaries by the quantity

        Args:
            iterable (list): The list of dictionaries to search in.
            key (str): The key to search for.
            value (int): The value to search for.

        Returns:
            dict: The item in the list of dictionaries.
        """
        for index, dict_ in enumerate(iterable):
            if key in dict_ and dict_[key] == value:
                # проверяем что он есть в бд каталога
                variation_id = QueriesCatalog().find_id_by_sku(dict_["barcode"], value)
                if variation_id != []:
                    if variation_id[0]["qty"] == value:
                        return {**variation_id[0], **dict_}

    def get_payload_for_update(self, schema, current_data, **kwargs):
        """Generate the payload for the body request using the schema

        Args:
            schema (dict): The schema to use for the body request.
            current_data (dict): The current data to update.
            **kwargs (dict): The kwargs to update the current data with.

        Returns:
            dict: The payload for the body request.
        """
        """Get the keys from the schema"""
        keys = list(schema.schema.keys())

        """Filter the current data to include only the keys defined in the schema"""
        data_for_update = {k: current_data.get(k) for k in keys}

        """Replace the values in the current data with the values from kwargs if they exist, in case of None - remove"""
        if kwargs is not None:
            for key in kwargs:
                if kwargs[key] is None:
                    data_for_update.pop(key)
                data_for_update[key] = kwargs[key]

        return data_for_update

    def random_birth_date(self):
        """
        Generates a random birth date within the last 100 years.

        Returns:
            str: A randomly generated birth date in the format "YYYY-MM-DD".
        """
        # Get the current date and time
        today = datetime.date.today()

        # Calculate the earliest possible year for a date
        earliest_year = today.year - 100

        # Generate a random year within the last 100 years
        year = random.randint(earliest_year, today.year)

        # Generate a random month and day (avoiding February 29th)
        month = random.randint(1, 12)
        while True:
            if month == 2 and random.randint(1, 28) > 28:
                break
            elif [month, 31] in [[1, 31], [3, 31], [5, 31], [7, 31], [8, 31], [10, 31]]:
                day = random.randint(1, 31)
                break
            else:
                day = random.randint(1, 30)

        # Format the date as "1997-01-22"
        date = f"{year}-{month:02d}-{day:02d}"

        return date

    def random_bearer_token(self, len=32):
        """
        Generates a random Bearer token of the specified length.

        Args:
            len (int): The length of the token. Defaults to 32.

        Returns:
            str: A randomly generated Bearer token.
        """
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(len))

    def decode_unicode(self, encoded_string):
        """
        Decodes a string from UTF-8 to Latin-1 encoding.

        Args:
            encoded_string (str): The string to decode.

        Returns:
            str: The decoded string.
        """
        decoded_string = encoded_string.encode("latin1").decode("utf-8")
        return decoded_string

    def code_unicode(self, cyrillic_string):
        """
        Encodes a string to UTF-8 to Latin-1 encoding.

        Args:
            cyrillic_string (str): The string to encode.

        Returns:
            str: The encoded string.
        """
        unicode_escaped = cyrillic_string.encode("utf-8").decode("latin1")
        return unicode_escaped

    def cookies_for_shop(self, name: str, value: str):
        """Prepare cookies for the page"""
        domain = os.getenv("SHOP_URL").replace("https://", "").replace("http://", "")
        return {"name": name, "value": value, "domain": f"{domain}", "path": "/"}


    def remove_flocktory_overlay(self, page):
        """Remove Flocktory widget"""
        # Ждем появления элемента с нужным атрибутом
        try:
            page.wait_for_selector('.flocktory-widget-overlay[data-showed-up="true"]', timeout=2000)

            # Удаляем элемент
            page.evaluate("""
                () => {
                    const element = document.querySelector('.flocktory-widget-overlay[data-showed-up="true"]');
                    element.remove();
                }
            """)
        except:
            print("Элемент с data-showed-up='true' не найден")

    def hex_to_rgb(self, hex_color: str) -> str:
        """
        Метод конвертирует цвет в формате HEX в формат RGB
        :param hex_color: Строка со значением цвета в формате HEX
        :return:
        """
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c * 2 for c in hex_color])

        if len(hex_color) != 6:
            raise ValueError("Неверный формат HEX цвета")

        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        return f"rgb({r}, {g}, {b})"
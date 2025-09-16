from befree.api_model import db_connection


class QueriesCatalog:
    def find_variation_by_availability_condition(
        self,
        ff_frozen: bool = False,
        omni_frozen: bool = False,
        omni2_frozen: bool = False,
        sfs_frozen: bool = False,
        city_id_in="any",
        city_id_out=None,
        qty_ff="> 0",
        qty_omni="any",
        qty_sfs="any",
        limit: int = 1,
        pickup_enabled_omni1: bool = True,
        conditions: list = [],
    ):
        """Запрос находит варианты по заданным условиям
        ff_frozen: bool = False, omni_frozen: bool = False, omni2_frozen: bool = False, sfs_frozen: bool = False, city_id_in = "any", city_id_out = None, qty_ff = 1, qty_omni = 1, qty_sfs = 1, limit: int = 1, pickup_enabled_omni1: bool = True
        ff_frozen: флаг заморозки для склада 3pl
        omni_frozen: флаг заморозки для склада омни
        omni2_frozen: флаг заморозки для склада омни2
        sfs_frozen: флаг заморозки для склада sfs
        city_id_in: id города для склада омни в котором есть товар
        city_id_out: id города для склада омни в котором нет товара
        qty_ff: количество для склада 3pl
        qty_omni: количество для склада омни
        qty_sfs: количество для склада sfs
        limit: количество вариантов
        pickup_enabled_omni1: флаг доступности омни1 в магазине
        conditions: дополнительные условия для поиска
        """
        params = " ".join(conditions)
        exists__omni_condition = f"""and (exists ( select variation_id 
                                        from product_inventories
                                        where variation_id = v.id
                                            and 
{f"product_inventories.city_id = {city_id_in}" if city_id_in != "any" else "product_inventories.store_id not in (1,2,500)"}
                                            group by variation_id
                                            having COUNT(*) = (
                                                    SELECT COUNT(*)
                                                    FROM product_inventories
                                                    join stores on stores.id = product_inventories.store_id 
                                                    WHERE variation_id = v.id and {f"product_inventories.city_id = {city_id_in}" if city_id_in != "any" else "product_inventories.store_id not in (1,2,500)"} and {"qty = 0" if qty_omni is None else f"qty {qty_omni}"} and stores.pickup_enabled_omni1 is {pickup_enabled_omni1}
                                                )
                                            ))
                                """
        not_exists_omni_condition = f"""and (not exists (
                            select variation_id
                            from product_inventories
                            where variation_id = v.id and product_inventories.city_id = {city_id_out}
                            group by variation_id
                            having COUNT(*) = (
                                SELECT COUNT(*)
                                FROM product_inventories
                                WHERE variation_id = v.id and product_inventories.city_id = {city_id_out} and product_inventories.qty > 0
                            )   
                         ))"""
        sfs_condition = ""
        if qty_sfs != "any" and qty_sfs is not None:
            sfs_condition = f"""and (exists (
								select variation_id
								from product_inventories
								 where variation_id = v.id
								 and product_inventories.store_id = 500 and qty {qty_sfs}
							)
						)"""
        if qty_sfs is None:
            sfs_condition = """and (exists (
								select variation_id
								from product_inventories
								 where variation_id = v.id
								 and product_inventories.store_id = 500 and qty = 0
							)or not exists(
								select variation_id
								from product_inventories
								 where variation_id = v.id
								 and product_inventories.store_id = 500
							) 
						)"""

        query = f"""select distinct pi2.variation_id
                    from variations v 
                    left join products p on p.id =v.product_id 
                    left join product_inventories pi2 on pi2.variation_id = v.id 
                    left join cities c on c.id = pi2.city_id 
                    where p.fulfilment_frozen is {ff_frozen} 
                        and p.omni2_frozen is {omni2_frozen} 
                        and p.omni_frozen is {omni_frozen} 
                        and p.sfs_frozen is {sfs_frozen} 
                        and pi2.store_id = 1 and {"pi2.qty = 0" if qty_ff is None else f"pi2.qty {qty_ff}"}
                        {sfs_condition}
                        {exists__omni_condition if qty_omni != "any" else ""}
                        {not_exists_omni_condition if city_id_out is not None else ""}
                    {params}
                """

        request = db_connection.catalog.get_data(query)[0:limit]
        return request

    def get_city_by_store(self, store_id):
        query = f"""
                select c.fias_id , c.golden_record 
                from cities c 
                join stores s on s.city_id =c.id 
                where s.id = {store_id}
           """

        request = db_connection.catalog.get_data(query)
        return request[0]["fias_id"], request[0]["golden_record"]

    def find_omni_stocks(self, qty):
        """Запрос находит товар в наличии на складах омни в заданном количестве. Товар также может быть в наличии на складе фулфилмента"""
        query = f"""
                    select pi2.variation_id, pi2.store_id, s.external_id  
                    from product_inventories pi2
                    join cities c on c.id = pi2.city_id 
                    join products p on p.id = pi2.product_id
                    join stores s on s.id = pi2.store_id 
                    where  pi2.city_id is not null and pi2.qty > {qty} and c.omni_2 = false and p.omni_frozen = false and s.pickup_enabled_omni1 = true
                    limit 1
                """
        request = db_connection.catalog.get_data(query)
        return request[0]["variation_id"], request[0]["store_id"], request[0]["external_id"]

    def find_omniAndSf_stocks(self, qty, city_id, store_id=1, conditions=""):
        """Запрос находит товар в наличии на складе ff и на складе омни в заданном городе для заданного количество"""
        params = " ".join(conditions)
        query = f"""
                    select distinct pi2.variation_id
                    from variations v 
                    join products p on p.id =v.product_id 
                    join product_inventories pi2 on pi2.variation_id = v.id 
                    join variation_attribute_values vav on vav.variation_id =v.id
                    where  p.omni_frozen = false
                        and (exists(select * from product_inventories
                                                                 where variation_id = v.id
                                                                    and (product_inventories.city_id = {city_id}  
                                                                    and product_inventories.qty >= {qty})))
                        and (exists(select * from product_inventories
                                                                 where variation_id = v.id
                                                                    and (product_inventories.store_id = {store_id}
                                                                    and product_inventories.qty >= {qty})))
                        {params}
                    limit 1
                """
        request = db_connection.catalog.get_data(query)
        return request[0]["variation_id"]

    def find_omni_stocks_by_city(self, city_fias_id):
        """Запрос возвращает варианты у которых количество больше или равно 3 для определенного города"""
        query = f"""
            select pi2.variation_id
            from product_inventories pi2 
            left join cities c on c.id = pi2.city_id 
            left join stores s on s.id = pi2.store_id 
            where pi2.qty >=3 and c.fias_id = '{city_fias_id}' and s.pickup_enabled_omni1 is true and s.deleted_at is null
        """

        request = db_connection.catalog.get_data(query)
        return request

    def find_stocks(self, store_id, qty):
        """Запрос возвращает id варианта в определенном магазине в заданном количестве"""
        query = """
                   select pi2.variation_id
                    from product_inventories pi2
                    join products p on p.id = pi2.product_id
                    where  pi2.store_id = 2 and pi2.qty > 2 and p.omni2_frozen = false and p.fulfilment_frozen = false
                    limit 1
                """
        request = db_connection.catalog.get_data(query)
        return request[0]["variation_id"]

    def store_by_city(self, city_id):
        """Запрос возвращает id и external_id магазина для заданного города"""
        query = f"""
            select distinct s.id,s.external_id 
            from stores s 
            join product_inventories pi2 on pi2.store_id = s.id
            where s.city_id = {city_id}  and s.deleted_at is null 
            limit 1
        """
        request = db_connection.catalog.get_data(query)
        return request[0]["id"], request[0]["external_id"]

    def find_omni2AndSf_out_of_stocks(self):
        """Запрос возвращает id варианта который не в наличии на складе 3pl, но может быть на складе омни"""
        query = """
                    select distinct pi2.variation_id
                    from variations v 
                    join products p on p.id =v.product_id 
                    join product_inventories pi2 on pi2.variation_id = v.id 
                    where  p.omni_frozen = false
                        and (exists(select * from product_inventories
                                                                 where variation_id = v.id
                                                                    and (product_inventories.store_id = 1  
                                                                    and product_inventories.qty = 0)))
                        and (exists(select * from product_inventories
                                                                 where variation_id = v.id
                                                                    and (product_inventories.store_id = 2
                                                                    and product_inventories.qty = 0)))
                    limit 1
                """
        request = db_connection.catalog.get_data(query)
        return request[0]["variation_id"]

    def find_total_out_of_stocks(self, omni_frozen: bool = False, ff_frozen: bool = False):
        """Запрос возвращает id варианта который не в наличии по всем складам"""
        query = f"""select distinct pi2.variation_id
                    from variations v 
                    join products p on p.id =v.product_id 
                    join product_inventories pi2 on pi2.variation_id = v.id 
                    where  p.omni_frozen = {omni_frozen} and p.fulfilment_frozen = {ff_frozen} and p.omni2_frozen = {ff_frozen}
                        and (exists(select * from product_inventories
                                                                 where variation_id = v.id
                                                                    and (product_inventories.store_id in (1, 2)
                                                                    and product_inventories.qty = 0)))
                        and (not exists(select * from product_inventories
                                                                 where variation_id = v.id
                                                                    and (product_inventories.store_id > 2 ))) """
        request = db_connection.catalog.get_data(query)
        return request[0]["variation_id"]

    def find_id_by_sku(self, sku, qty):
        """Запрос возвращает id варианта, цену level 0 и количество по заданному и ску и заданному количеству по складу 3pl"""
        query = f"""select v.id, v.calculated_price_level_0, pri.qty 
                from variations v 
                join product_inventories pri on pri.variation_id = v.id   
                where v.sku = '{sku}' and pri.store_id = 1 and pri.qty >= {qty}"""
        response = db_connection.catalog.get_data(query)
        return response

    def get_product_by_variation(self, variation_id):
        """Запрос возвращает артикул, id продукта, id колор кода и id размера для продукта по заданному ску"""
        query = f"""
                    select p.article , p.id, v.color_code_id , v.size_id, p.category_id
                    from products p
                    join variations v on v.product_id  = p.id
                    where v.id = {variation_id}
               """
        response = db_connection.catalog.get_data(query)
        return response[0]

    def find_stocks_omni_by_variation(self, variation_id: int, value_omni2: bool, qty: int):
        """Запрос возвращает id города и стора по заданному id варианта и количеству с заданным флагом омни2"""
        query = f"""select pi2.city_id , pi2.store_id 
                    from product_inventories pi2 
                    join cities c on c.id = pi2.city_id 
                    where pi2.variation_id = {variation_id} and pi2.qty >{qty} and c.omni_2 = {value_omni2}
                    limit 1
                       """
        response = db_connection.catalog.get_data(query)
        return response[0]

    def find_stocks_only_omni(self, qty: int, value_omni2: bool = False, frozen: bool = False):
        """Запрос возвращает id варианта который есть только в омни, id магазина и количество по заданному флагу омни2 и количеству с учетом флага заморозки"""
        query = f"""select distinct pi2.variation_id , pi2.store_id , pi2.qty 
                    from variations v 
                    join products p on p.id =v.product_id 
                    join product_inventories pi2 on pi2.variation_id = v.id 
                    join cities c on c.id = pi2.city_id 
                    where  p.omni_frozen = {frozen} and c.omni_2 = {value_omni2} and pi2.store_id > 2 and pi2.qty >= {qty}
                        and (exists(select * from product_inventories
                                                                 where variation_id = v.id
                                                                    and (product_inventories.store_id = 1  
                                                                    and product_inventories.qty = 0)))
                                                               limit 1
                                                   
                       """
        response = db_connection.catalog.get_data(query)
        return response[0]

    def find_stocks_only_ff(self, qty: int, frozen: bool = False):
        """Запрос возвращает id варианта который есть только в ff, id магазина и количество по заданному количеству с учетом флага заморозки"""
        query = f"""select distinct pi2.variation_id , pi2.store_id , pi2.qty 
                    from variations v 
                    left join products p on p.id =v.product_id 
                    left join product_inventories pi2 on pi2.variation_id = v.id 
                    left join cities c on c.id = pi2.city_id 
                    where p.omni2_frozen = {frozen} and p.fulfilment_frozen = {frozen} and pi2.store_id = 1 and pi2.qty > {qty}
                        and (exists ( select variation_id from product_inventories
                                         where variation_id = v.id
                                            and product_inventories.store_id > 2             
                                            group by variation_id
                                            having COUNT(*) = (
                                                    SELECT COUNT(*)
                                                    FROM product_inventories
                                                    WHERE variation_id = v.id and store_id > 2 and qty = 0
                                                )
                                            ))
                                       limit 1                       """
        response = db_connection.catalog.get_data(query)
        return response[0]

    def find_in_product_inventories(self, qty):
        """Запрос возвращает id варианта, id продукта, id магазина и id города по заданному количеству"""
        query = f"""select pi2.variation_id , pi2.product_id , pi2.store_id , pi2.city_id
                    from product_inventories pi2 
                    where pi2.qty >= {qty}
                    limit 1
                  """
        response = db_connection.catalog.get_data(query)
        return (
            response[0]["variation_id"],
            response[0]["product_id"],
            response[0]["store_id"],
            response[0]["city_id"],
        )

    def count_in_product_inventories_by_key(self, key, value, condition="="):
        """Запрос возвращает количество записей из таблицы product_inventories по заданному параметру"""
        query = f"""select count(*)
                    from product_inventories  
                    where {key} {condition} {value}
                          """
        response = db_connection.catalog.get_data(query)
        return response[0]["count"]

    def count_in_product_inventories_by_keys(self, conditions):
        """Запрос возвращает количество записей из таблицы product_inventories по заданным параметрам"""
        params = " ".join(conditions)
        query = f"""select count(*)
                    from product_inventories
                    where {params}
                          """
        response = db_connection.catalog.get_data(query)
        return response[0]["count"]

    def sum_in_product_inventories_by_keys(self, sum_colummn, conditions):
        """Запрос возвращает сумму записей из таблицы product_inventories по заданным параметрам"""
        params = " ".join(conditions)
        query = f"""select sum({sum_colummn})
                    from product_inventories
                    where {params}
                          """
        response = db_connection.catalog.get_data(query)
        return response[0]["sum"]

    def get_compilation(self, param, value, condition):
        """Запрос возвращает одну запись id компиляции, слаг и гендер по заданному условиям"""
        existing_compilation_query = f"""
                    select c.id, c.slug, c.gender 
                    from compilations c 
                    where c.deleted_at is null and {param} {condition} {value}
                    order by c.products_count desc
                    limit 1
                """
        compilation = db_connection.catalog.get_data(existing_compilation_query)

        return compilation[0]["id"], compilation[0]["slug"], compilation[0]["gender"]

    def get_compilation_by_conditions(self, conditions):
        """Запрос возвращает одну запись id компиляции, слаг и гендер по заданным условиям"""
        params = " ".join(conditions)
        existing_compilation_query = f"""
                    select c.id, c.slug, c.gender 
                    from compilations c 
                    where c.deleted_at is null and {params}
                    order by c.products_count desc
                    limit 1
                """
        compilation = db_connection.catalog.get_data(existing_compilation_query)

        return compilation[0]["id"], compilation[0]["slug"], compilation[0]["gender"]

    def get_product_by_conditions(self, conditions):
        """Запрос возвращает одну запись id продукта и артикул по заданным условиям"""
        params = " ".join(conditions)
        query = f"""
                    select  id, article 
                    from products p 
                    where {params} 
                    limit 1
                """
        return db_connection.catalog.get_data(query)[0]

    def check_frozen(self, article):
        """Запрос возвращает статус заморозки по разным типам складов для определенного артикула"""
        query = f"""
                    select  fulfilment_frozen , omni2_frozen , omni_frozen , sfs_frozen
                    from products p 
                    where article = '{article}'
                """
        return db_connection.catalog.get_data(query)[0]

    def get_product_articles(self, limit = 10):
        """Запрос возвращает список артикулов, которые не удалены"""
        query = f"""
            select p.article 
            from products p  
            where p.deleted_at is null
            order by p.id desc 
            limit {limit}
        """
        return db_connection.catalog.get_data(query)

    def get_variation(self, id):
        query = f"""
                    select *
                    from variations v 
                    where id = {id}
                """
        return db_connection.catalog.get_data(query)[0]

    def get_cities_with_stock(self):
        """Запрос возвращает список городов, в которых есть товар на складе omni"""
        query = """
            select distinct vi.city_id
            from variation_inventories vi
            where vi.city_id is not null
        """
        return db_connection.catalog.get_data(query)

    def get_active_categories(self):
        """Запрос возвращает список активных компиляций, котрые являются категориями"""
        query = """
                    select c.id
                    from compilations c 
                    where c.deleted_at is null and c.is_category is true
                """
        return db_connection.catalog.get_data(query)

    def get_active_compilations(self):
        """Запрос возвращает список активных компиляций"""
        query = """
                    select c.id
                    from compilations c 
                    where c.deleted_at is null
                """
        return db_connection.catalog.get_data(query)

    def get_omni_stores_with_stock(self, variation_id, city_id):
        """Запрос возвращает список магазинов, в которых есть товар на складе omni в определенном городе"""
        query = f"""
            select pi2.store_id
            from product_inventories pi2
            where pi2.variation_id = {variation_id} and pi2.city_id = {city_id} and pi2.qty > 0
        """
        return db_connection.catalog.get_data(query)

    def query_by_conditions(self, table, conditions=""):
        params = " ".join(conditions)
        query = f"""
                    select *
                    from {table} 
                    where {params}
                """
        return db_connection.catalog.get_data(query)

    def entity_by_id(self, table, id):
        """Запрос возвращает данные по заданному id в конкретной таблице"""
        query = f"""
                    select *
                    from {table} 
                    where id = {id}
                """
        return db_connection.catalog.get_data(query)[0]

    def get_data_for_product_card(self, conditions=None, join_conditions=None):
        """Запрос возвращает данные по заданному условию и возвращает данные для формирования урла страницы товара:
        артикул, id размера и id роста"""
        if conditions is None:
            conditions = []

        if join_conditions is None:
            join_conditions = []

        params = " ".join(conditions)
        join_conditions = " ".join(join_conditions)
        query = f"""
                    select p.article, v.color_code_id, v.size_id, v.height_id
                    from variations v 
                    join products p on p.id = v.product_id
                    {join_conditions}
                    where v.deleted_at is null and p.deleted_at is null {params}
                    limit 1
                """
        result = db_connection.catalog.get_data(query)
        return result[0] if result else print("Не найден товар по переданным условиям")


    def get_city_data(self, title):
        """
        Возвращает fias_id и golder_record по названию города
        """
        query = f"""
                    SELECT fias_id, golden_record FROM cities WHERE title = '{title}';      
                """
        result = db_connection.catalog.get_data(query)
        return result[0] if result else print("Не найден товар по переданным условиям")

    def get_empty_description_product(self):
        """
        Получаем товар с пустым описанием, если такого нет,
        то убираем описание у первого в БД товара и возвращаем его
        """

        query = f"""
                    SELECT p.article
                    FROM attribute_values av
                    JOIN variation_attribute_values vav 
                        ON av.id = vav.attribute_value_id
                    JOIN products p
                        ON vav.product_id = p.id
                    WHERE av.attribute_id = 103
                      AND av.value_string = ''
                      AND av.value_text = '';
                """

        result = db_connection.catalog.get_data(query)
        if result:
            return result[0]

        update_query = """
                UPDATE attribute_values
                SET value_string = '', value_text = ''
                WHERE id = (
                    SELECT id
                    FROM attribute_values
                    WHERE attribute_id = 103
                    ORDER BY id DESC
                    LIMIT 1
                )
                RETURNING id;
            """

        db_connection.catalog.update_data(update_query)
        result = db_connection.catalog.get_data(query)
        return result[0] if result else None

    def get_description_with_hyperlink(self):
        """
        Получаем артикул товара у которого есть гипертекст в описании
        """
        query = """
            SELECT p.article
                    FROM attribute_values av
                    JOIN variation_attribute_values vav 
                        ON av.id = vav.attribute_value_id
                    JOIN products p
                        ON vav.product_id = p.id
                    WHERE av.attribute_id = 103
                      AND av.value_text LIKE '%[%]%'; 
        """

        result = db_connection.catalog.get_data(query)
        return result[0] if result else None


    def get_description_with_special_symb(self):
        """
        Получение товара со спецсимволами, если такого нет,
        то добавляем спецсимволы в описание к случайному товару и получаем его
        """
        query = """
            SELECT p.article
                    FROM attribute_values av
                    JOIN variation_attribute_values vav 
                        ON av.id = vav.attribute_value_id
                    JOIN products p
                        ON vav.product_id = p.id
                    WHERE av.attribute_id = 103
                      AND av.value_text LIKE 'Text with special symbols:%'
                      AND av.value_string LIKE 'Text with special symbols:%';
        """

        update_query = """
            UPDATE attribute_values
                    SET value_text = E'Text with special symbols: [\"\\<>&%$#@!?/\\[\\](){};:]',
                        value_string = E'Text with special symbols: [\"\\<>&%$#@!?/\\[\\](){};:]'
                    WHERE id = (
                        SELECT id
                        FROM attribute_values
                        WHERE attribute_id = 103
                        ORDER BY id DESC
                        LIMIT 1
                    )
        """

        result = db_connection.catalog.get_data(query)
        if result:
            return result[0]

        db_connection.catalog.update_data(update_query)
        result = db_connection.catalog.get_data(query)
        return result[0] if result else None



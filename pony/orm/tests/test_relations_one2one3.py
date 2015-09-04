from __future__ import absolute_import, print_function, division

import unittest

from pony.orm.core import *
from pony.orm.tests.testutils import *

class TestOneToOne3(unittest.TestCase):
    def setUp(self):
        self.db = Database('sqlite', ':memory:')

        class Person(self.db.Entity):
            name = Required(unicode)
            passport = Optional("Passport", cascade_delete=True)

        class Passport(self.db.Entity):
            code = Required(unicode)
            person = Required("Person")

        self.db.generate_mapping(create_tables=True)

        with db_session:
            p1 = Person(name='John')
            Passport(code='123', person=p1)

    def tearDown(self):
        self.db = None

    @db_session
    def test_1(self):
        obj = select(p for p in self.db.Person if p.passport.id).first()
        self.assertEqual(obj.name, 'John')
        self.assertEqual(obj.passport.code, '123')

    @db_session
    def test_2(self):
        select(p for p in self.db.Person if p.passport is None)[:]
        sql = self.db.last_sql
        self.assertEqual(sql, '''SELECT "p"."id", "p"."name"
FROM "Person" "p"
  LEFT JOIN "Passport" "passport-1"
    ON "p"."id" = "passport-1"."person"
WHERE "passport-1"."id" IS NULL''')

    @db_session
    def test_3(self):
        select(p for p in self.db.Person if not p.passport)[:]
        sql = self.db.last_sql
        self.assertEqual(sql, '''SELECT "p"."id", "p"."name"
FROM "Person" "p"
  LEFT JOIN "Passport" "passport-1"
    ON "p"."id" = "passport-1"."person"
WHERE "passport-1"."id" IS NULL''')

    @db_session
    def test_4(self):
        select(p for p in self.db.Person if p.passport)[:]
        sql = self.db.last_sql
        self.assertEqual(sql, '''SELECT "p"."id", "p"."name"
FROM "Person" "p"
  LEFT JOIN "Passport" "passport-1"
    ON "p"."id" = "passport-1"."person"
WHERE "passport-1"."id" IS NOT NULL''')

    @db_session
    def test_5(self):
        p = self.db.Person.get(name='John')
        p.delete()
        flush()
        sql = self.db.last_sql
        self.assertEqual(sql, '''DELETE FROM "Person"
WHERE "id" = ?
  AND "name" = ?''')        

if __name__ == '__main__':
    unittest.main()
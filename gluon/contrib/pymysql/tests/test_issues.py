import pymysql
from pymysql.tests import base

try:
    import imp
    reload = imp.reload
except AttributeError:
    pass

import datetime

class TestOldIssues(base.PyMySQLTestCase):
    def test_issue_3(self):
        """ undefined methods datetime_or_None, date_or_None """
        conn = self.connections[0]
        c = conn.cursor()
        c.execute("create table issue3 (d date, t time, dt datetime, ts timestamp)")
        try:
            c.execute("insert into issue3 (d, t, dt, ts) values (%s,%s,%s,%s)", (None, None, None, None))
            c.execute("select d from issue3")
            self.assertEqual(None, c.fetchone()[0])
            c.execute("select t from issue3")
            self.assertEqual(None, c.fetchone()[0])
            c.execute("select dt from issue3")
            self.assertEqual(None, c.fetchone()[0])
            c.execute("select ts from issue3")
            self.assertTrue(isinstance(c.fetchone()[0], datetime.datetime))
        finally:
            c.execute("drop table issue3")

    def test_issue_4(self):
        """ can't retrieve TIMESTAMP fields """
        conn = self.connections[0]
        c = conn.cursor()
        c.execute("create table issue4 (ts timestamp)")
        try:
            c.execute("insert into issue4 (ts) values (now())")
            c.execute("select ts from issue4")
            self.assertTrue(isinstance(c.fetchone()[0], datetime.datetime))
        finally:
            c.execute("drop table issue4")

    def test_issue_5(self):
        """ query on information_schema.tables fails """
        con = self.connections[0]
        cur = con.cursor()
        cur.execute("select * from information_schema.tables")

    def test_issue_6(self):
        """ exception: TypeError: ord() expected a character, but string of length 0 found """
        conn = pymysql.connect(host="localhost",user="root",passwd="",db="mysql")
        c = conn.cursor()
        c.execute("select * from user")
        conn.close()

    def test_issue_8(self):
        """ Primary Key and Index error when selecting data """
        conn = self.connections[0]
        c = conn.cursor()
        c.execute("""CREATE TABLE `test` (`station` int(10) NOT NULL DEFAULT '0', `dh`
datetime NOT NULL DEFAULT '0000-00-00 00:00:00', `echeance` int(1) NOT NULL
DEFAULT '0', `me` double DEFAULT NULL, `mo` double DEFAULT NULL, PRIMARY
KEY (`station`,`dh`,`echeance`)) ENGINE=MyISAM DEFAULT CHARSET=latin1;""")
        try:
            self.assertEqual(0, c.execute("SELECT * FROM test"))
            c.execute("ALTER TABLE `test` ADD INDEX `idx_station` (`station`)")
            self.assertEqual(0, c.execute("SELECT * FROM test"))
        finally:
            c.execute("drop table test")

    def test_issue_9(self):
        """ sets DeprecationWarning in Python 2.6 """
        try:
            reload(pymysql)
        except DeprecationWarning:
            self.fail()

    def test_issue_10(self):
        """ Allocate a variable to return when the exception handler is permissive """
        conn = self.connections[0]
        conn.errorhandler = lambda cursor, errorclass, errorvalue: None
        cur = conn.cursor()
        cur.execute( "create table t( n int )" )
        cur.execute( "create table t( n int )" )

    def test_issue_13(self):
        """ can't handle large result fields """
        conn = self.connections[0]
        cur = conn.cursor()
        cur.execute("create table issue13 (t text)")
        try:
            # ticket says 18k
            size = 18*1024
            cur.execute("insert into issue13 (t) values (%s)", ("x" * size,))
            cur.execute("select t from issue13")
            # use assert_ so that obscenely huge error messages don't print
            r = cur.fetchone()[0]
            self.assert_("x" * size == r)
        finally:
            cur.execute("drop table issue13")

    def test_issue_14(self):
        """ typo in converters.py """
        self.assertEqual('1', pymysql.converters.escape_item(1, "utf8"))
        self.assertEqual('1', pymysql.converters.escape_item(1L, "utf8"))

        self.assertEqual('1', pymysql.converters.escape_object(1, "utf8"))
        self.assertEqual('1', pymysql.converters.escape_object(1L, "utf8"))

    def test_issue_15(self):
        """ query should be expanded before perform character encoding """
        conn = self.connections[0]
        c = conn.cursor()
        c.execute("create table issue15 (t varchar(32))")
        try:
            c.execute("insert into issue15 (t) values (%s)", (u'\xe4\xf6\xfc'))
            c.execute("select t from issue15")
            self.assertEqual(u'\xe4\xf6\xfc', c.fetchone()[0])
        finally:
            c.execute("drop table issue15")

    def test_issue_16(self):
        """ Patch for string and tuple escaping """
        conn = self.connections[0]
        c = conn.cursor()
        c.execute("create table issue16 (name varchar(32) primary key, email varchar(32))")
        try:
            c.execute("insert into issue16 (name, email) values ('pete', 'floydophone')")
            c.execute("select email from issue16 where name=%s", ("pete",))
            self.assertEqual("floydophone", c.fetchone()[0])
        finally:
            c.execute("drop table issue16")

    def test_issue_17(self):
        """ could not connect mysql use passwod """
        conn = self.connections[0]
        host = self.databases[0]["host"]
        db = self.databases[0]["db"]
        c = conn.cursor()
        # grant access to a table to a user with a password
        c.execute("create table issue17 (x varchar(32) primary key)")
        try:
            c.execute("insert into issue17 (x) values ('hello, world!')")
            c.execute("grant all privileges on issue17 to issue17user identified by '1234'")
            
            conn2 = pymysql.connect(host=host, user="issue17user", passwd="1234", db=db)
            c2 = conn2.cursor()
            c2.execute("select x from issue17")
            self.assertEqual("hello, world!", c2.fetchone()[0])
        finally:
            c.execute("drop table issue17")

class TestNewIssues(base.PyMySQLTestCase):
    def test_issue_34(self):
        try:
            pymysql.connect(host="localhost", port=1237, user="root")
            self.fail()
        except pymysql.OperationalError, e:
            self.assertEqual(2003, e.args[0])
        except:
            self.fail()

    def test_issue_33(self):
        conn = pymysql.connect(host="localhost", user="root", db=self.databases[0]["db"], charset="utf8")
        c = conn.cursor()
        try:
            c.execute("create table hei\xc3\x9f (name varchar(32))")
            c.execute("insert into hei\xc3\x9f (name) values ('Pi\xc3\xb1ata')")
            c.execute("select name from hei\xc3\x9f")
            self.assertEqual("Pi\xc3\xb1ata", c.fetchone()[0].encode("utf8"))
        finally:
            c.execute("drop table hei\xc3\x9f")

    # Will fail without manual intervention:
    #def test_issue_35(self):
    #
    #    conn = self.connections[0]
    #    c = conn.cursor()
    #    print "sudo killall -9 mysqld within the next 10 seconds"
    #    try:
    #        c.execute("select sleep(10)")
    #        self.fail()
    #    except pymysql.OperationalError, e:
    #        self.assertEqual(2013, e.args[0])

    def test_issue_36(self):
        conn = self.connections[0]
        c = conn.cursor()
        # kill connections[0]
        original_count = c.execute("show processlist")
        kill_id = None
        for id,user,host,db,command,time,state,info in c.fetchall():
            if info == "show processlist":
                kill_id = id
                break
        # now nuke the connection
        conn.kill(kill_id)
        # make sure this connection has broken
        try:
            c.execute("show tables")
            self.fail()
        except:
            pass
        # check the process list from the other connection
        self.assertEqual(original_count - 1, self.connections[1].cursor().execute("show processlist"))
        del self.connections[0]

    def test_issue_37(self):
        conn = self.connections[0]
        c = conn.cursor()
        self.assertEqual(1, c.execute("SELECT @foo"))
        self.assertEqual((None,), c.fetchone())
        self.assertEqual(0, c.execute("SET @foo = 'bar'"))
        c.execute("set @foo = 'bar'")

    def test_issue_38(self):
        conn = self.connections[0]
        c = conn.cursor()
        datum = "a" * 1024 * 1024 * 64
        c.execute("create table issue38 (id integer, data mediumblob)")
        try:
            c.execute("insert into issue38 values (1, %s)", datum)
        finally:
            c.execute("drop table issue38")
__all__ = ["TestOldIssues", "TestNewIssues"]

if __name__ == "__main__":
    import unittest
    unittest.main()

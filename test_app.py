import unittest
from app import app, db, Search


class AppTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_index_page(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Узнать погоду в городе", response.data.decode("utf-8"))

    def test_search_city(self):
        response = self.app.post("/", data={"city": "Moscow"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Moscow", response.data)

    def test_search_history(self):
        self.app.post("/", data={"city": "Moscow"})
        self.app.post("/", data={"city": "London"})
        response = self.app.get("/")
        self.assertIn(b"Moscow", response.data)
        self.assertIn(b"London", response.data)

    def test_search_history_count(self):
        self.app.post("/", data={"city": "Moscow"})
        self.app.post("/", data={"city": "Moscow"})
        response = self.app.get("/")
        self.assertIn("2 раз(а)", response.data.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()

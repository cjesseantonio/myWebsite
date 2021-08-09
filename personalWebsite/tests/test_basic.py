import unittest, sys
#from .. personalWebsite import web_page

sys.path.append('myWebsite/myWebsite') # imports python file from parent directory
from web_page import app #imports flask app object

class BasicTests(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        self.app = app.test_client()

    ###############
    #### tests ####
    ###############

    def test_home_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def test_about_page(self):
        response = self.app.get('/about', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def test_resume_page(self):
        response = self.app.get('/resume', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
    def test_contact_page(self):
        response = self.app.get('/contact', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
    
#Add more tests to cover all your website pages
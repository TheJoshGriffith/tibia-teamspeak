import TeamSpeakConnector, TibiaCrawler, os, CherryPyServer, cherrypy


tsc = TeamSpeakConnector.TeamSpeakConnector()
tc = TibiaCrawler.TibiaCrawler("Olympa")
tc.start()
cherrypy.quickstart(CherryPyServer.HelloWorld(tsc))
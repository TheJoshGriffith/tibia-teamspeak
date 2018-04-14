import TeamSpeakConnector, TibiaCrawler, os, CherryPyServer, cherrypy


tsc = TeamSpeakConnector.TeamSpeakConnector()
tc = TibiaCrawler.TibiaCrawler()
tc.start()
cherrypy.quickstart(CherryPyServer.HelloWorld(tsc))
from aqxWeb.dao.userDAOv2 import userDAO
from aqxWeb.dao.systemDAOv2 import systemDAO
from aqxWeb.dao.metadataDAOv2 import metadataDAO

from collections import defaultdict

import json


class API:
    def __init__(self, conn):
        self.conn = conn
        self.systemDAO = systemDAO(self.conn)
        self.userDAO = userDAO(self.conn)
        self.metadataDAO = metadataDAO(self.conn)

    # SystemAPI

    def getSystem(self, systemUID):

        result = self.systemDAO.getSystem(systemUID)
        systemID = result[0]
        # Get the crops
        results = self.systemDAO.getCropsForSystem(systemID)
        crops = []
        for crop in results:
            crops.append({
                'name': crop[0],
                'count': crop[1]
            })
        # Get the grow bed media
        results = self.systemDAO.getGrowBedMediaForSystem(systemID)
        media = []
        for medium in results:
            media.append({
                'name': medium[0],
                'count': medium[1]
            })
        # Get the organisms
        results = self.systemDAO.getOrganismsForSystem(systemID)
        organisms = []
        for organism in results:
            organisms.append({
                'name': organism[0],
                'count': organism[1]
            })
        # Recompile the system
        system = {
            'ID': result[0],
            'UID': result[1],
            'user': result[2],
            'name': result[3],
            'creationTime': str(result[4]),
            'startDate': str(result[5]),
            'location': {'lat': str(result[6]), 'lng': str(result[7])},
            'technique': result[8],
            'status': result[9],
            'gbMedia': media,
            'crops': crops,
            'organisms': organisms,
        }
        return json.dumps(system)

    def getSystemsForUser(self, userID):
        systems = []
        results = self.systemDAO.getSystemsForUser(userID)
        for result in results:
            systems.append({
                'ID:': result[0],
                'UID': result[1],
                'name': result[2]
            })
        return json.dumps(systems)

    def createSystem(self, system):
        systemInfo = self.systemDAO.createSystem(system)
        return json.dumps(systemInfo)

    # UserAPI

    def getUserID(self, googleID):
        userID = self.userDAO.getUserID(googleID)
        return json.dumps({'userID': userID})

    def hasUser(self, googleID):
        count = self.userDAO.hasUser(googleID)
        return json.dumps({'hasUser': count == 1})

    # Metadata API

    def getEnums(self):
        results = self.metadataDAO.getEnums()
        enums = defaultdict(list)
        for result in results:
            table = result[0]
            enums[table] = []
        for result in results:
            table = result[0]
            enums[table].append({
                'ID': result[1],
                'name': result[2]
            })
        return json.dumps(enums)

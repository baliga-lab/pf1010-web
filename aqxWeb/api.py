from aqxWeb.dao.users import UserDAO
from aqxWeb.dao.systems import SystemDAO
from aqxWeb.dao.metadata import MetadataDAO
from aqxWeb.dao.annotations import AnnotationDAO
from aqxWeb.dao.subscriptions import SubscriptionDAO
from aqxWeb.dao.measurements import MeasurementDAO

from collections import defaultdict

import json


class API:

    def __init__(self, app):
        self.systemDAO = SystemDAO(app)
        self.userDAO = UserDAO(app)
        self.metadataDAO = MetadataDAO(app)
        self.subscriptionDAO = SubscriptionDAO(app)
        self.annotationDAO = AnnotationDAO(app)
        self.measurementDAO = MeasurementDAO(app)

    ###########################################################################
    # SystemAPI
    ###########################################################################

    def get_system(self, systemUID):

        result = self.systemDAO.get_system(systemUID)
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
        # Get the status
        status = self.systemDAO.getStatusForSystem(systemUID)[0]
        # Recompile the system
        return {
            'ID': result[0],
            'UID': result[1],
            'user': result[2],
            'name': result[3],
            'creationTime': str(result[4]),
            'startDate': str(result[5]),
            'location': {'lat': str(result[6]), 'lng': str(result[7])},
            'technique': result[8],
            'status': status,
            'gbMedia': media,
            'crops': crops,
            'organisms': organisms,
        }

    def getSystemsForUser(self, userID):
        systems = []
        results = self.systemDAO.getSystemsForUser(userID)
        for result in results:
            systems.append({
                'ID': result[0],
                'UID': result[1],
                'name': result[2]
            })
        return json.dumps(systems)

    def create_system(self, system):
        """this is just a delegation to the DAO, no JSON serialization
        because it reduces reusability"""
        return self.systemDAO.create_system(system)

    def update_system(self, system):
        """this is just a delegation to the DAO, no JSON serialization
        because it reduces reusability"""
        return self.systemDAO.update_system(system)

    ###########################################################################
    # UserAPI
    ###########################################################################

    def getUserID(self, googleID):
        userID = self.userDAO.getUserID(googleID)
        return json.dumps({'userID': userID})

    def hasUser(self, googleID):
        count = self.userDAO.hasUser(googleID)
        return json.dumps({'hasUser': count == 1})

    def createUser(self, googleProfile):
        userID = self.userDAO.createUser(googleProfile)
        return json.dumps({'userID': userID})

    ###########################################################################
    # MetadataAPI
    ###########################################################################

    def catalogs(self):
        results = self.metadataDAO.catalogs()
        enums = defaultdict(list)
        for result in results:
            table = result[0]
            if not enums[table]:
                enums[table] = []
            enums[table].append({
                'ID': result[1],
                'name': result[2]
            })
        return enums

    ###########################################################################
    # AnnotationAPI
    ###########################################################################

    def getReadableAnnotation(self, annotationID):
        readable = self.annotationDAO.getReadableAnnotation(annotationID)
        return json.dumps(readable)

    def getReadableAnnotations(self):
        map = {}
        results = self.annotationDAO.getReadableAnnotations()
        for result in results:
            map[result[0]] = result[1:3]
        return json.dumps(map)

    def addAnnotation(self, annotation):
        rowID = self.annotationDAO.addAnnotation(annotation)
        return json.dumps({rowID: rowID})

    def getAnnotationsForSystem(self, systemID):
        annotations = []
        results = self.annotationDAO.getAnnotationsForSystem(systemID)
        for result in results:
            annotations.append({
                'key': result[0],
                'value': result[1],
                'description': result[2]
            })
        return json.dumps(annotations)

    ###########################################################################
    # SubscriptionAPI
    ###########################################################################

    def subscribe(self, email):
        subscriptionID = self.subscriptionDAO.subscribe(email)
        return json.dumps({subscriptionID: subscriptionID})

    ###########################################################################
    # MeasurementAPI
    ###########################################################################

    def latest_readings_for_system(self, systemUID):
        readings = self.measurementDAO.latest_readings_for_system(systemUID)
        return json.dumps(readings)

    def submit_reading(self, measurementType, systemUID, reading):
        rowID = self.measurementDAO.submit_reading(measurementType, systemUID, reading)
        return json.dumps({rowID: rowID})

    def measurement_types(self):
        return json.dumps(self.measurementDAO.measurement_types())

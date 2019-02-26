from enum import Enum


class WordstatMethod(Enum):
    CreateNewWordstatReport = 'CreateNewWordstatReport'
    DeleteWordstatReport = 'DeleteWordstatReport'
    GetWordstatReport = 'GetWordstatReport'
    GetWordstatReportList = 'GetWordstatReportList'


class FieldName(Enum):
    StatusReport = 'StatusReport'
    ReportID = 'ReportID'
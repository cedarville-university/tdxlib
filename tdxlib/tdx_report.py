import json
from typing import Optional
from enum import Enum
import tdxlib.tdx_api_exceptions
import tdxlib.tdx_utils
import datetime
from typing_extensions import TypedDict
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import tdxlib.tdx_report_integration

class OrderByColumn(TypedDict):
    ColumnLabel: str
    ColumnName: str
    IsAscending: bool
class ChartSetting(TypedDict):
    Axis: Optional[str]
    ColumnLabel: Optional[str]
    ColumnName: Optional[str]
class ColumnDataType(Enum):
    GenericData = 0
    String = 1
    Integer = 2
    Decimal = 3
    Currency = 4
    Percentage = 5
    Date = 6
    DateAndTime = 7
    Boolean = 8
    TimeSpan = 9
    ProjectHealth = 10
    Html = 11
class AggregateFunction(Enum):
    NONE = 0
    Average = 1
    Count = 2
    Maximum = 3
    Minimum = 4
    Sum = 5
class ComponentFunction(Enum):
    NONE = 0
    Year = 1
    MonthYear = 2
    WeekYear = 3
    Hour = 4
    HourWeek = 5
    HourMonth = 6
class DisplayColumn(TypedDict):
    HeaderText: str
    ColumnName: str
    DataType: ColumnDataType
    SortColumnExpression: Optional[str]
    SortColumnName: Optional[str]
    SortDataType: ColumnDataType
    Aggregate: AggregateFunction
    Component: ComponentFunction
    FooterExpression: Optional[str]
class TDXReportData(TypedDict):
    Description: Optional[str]
    MaxResults: int
    DisplayedColumns: Optional[list[DisplayColumn]]
    SortOrder: Optional[list[OrderByColumn]]
    ChartType: Optional[str]
    ChartSettings: Optional[list[ChartSetting]]
    DataRows: Optional[list[dict[str, object]]]
    ID: int
    Name: str
    CreatedUid: Optional[str]
    CreatedFullName: str
    CreatedDate: datetime.datetime
    OwningGroupID: Optional[int]
    OwningGroupName: str
    SystemAppName: str
    PlatformAppID: int
    PlatformAppName: Optional[str]
    ReportSourceID: int
    ReportSourceName: str
    Uri: str
class TDXReport(TypedDict):
    report_data: TDXReportData
    tdx_api: 'tdxlib.tdx_report_integration.TDXReportIntegration'
    def __repr__(self):
        return str(self.report_data.__dict__)
    
    def __str__(self):
        return json.dumps(self)
    
    def __init__(self, integration: 'tdxlib.tdx_report_integration.TDXReportIntegration', json: str):
        self.tdx_api = integration
        self.report_data = json.loads(json)
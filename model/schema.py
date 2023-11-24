from enum import Enum
from typing import Dict, List
from bson import ObjectId
from pydantic import BaseModel, Field

class NewUser(BaseModel):
    # account_id: List[str] = []
    account_ids: List[str]
    first_name: str
    last_name: str
    email: str
    timezone: str
    is_Agreed_To_Terms: bool = None
    is_news_letter_subscribed: bool = None
    password: str
    confirm_password: str
    token: str

class BrokerEnum(str, Enum):
    mt4 = 'mt4'
    mt5 = 'mt5'

class Account(BaseModel):
    account_id: str  # Reference to User document ID
    login: int = Field(..., description="Login is required")
    broker: BrokerEnum = Field(..., description="Broker must be either 'mt4' or 'mt5'")
    password: str = Field(..., description="Password is required")
    server: str = Field(..., description="Server is required")
    

class Trade(BaseModel):
    # account_id: ObjectId  # Reference to Account document ID
    Login:int
    symbol: str
    volume: float
    openPrice: float
    takeProfit: float
    stopLoss: float
    currentPrice: float
    Type: str
    ticket: int
    tradeTime: str
    closingTime: str
    isTradeClosed: bool
    currentProfit: float
    currentTime: str

class TradeList(BaseModel):
    trades: List[Trade]

class TDescription(BaseModel):
    Trade_Frequency: str
    Profit_Discrepancy: str
    Win_Rates: str
    Average_Profits: str
    Risk_Reward_Ratios_RRR: str
    Conclusion: str

class LongShortComparison(BaseModel):
    description: TDescription
    suggestion: str

class ResultsByDaysDescription(BaseModel):
    Monday: str
    Tuesday: str
    Wednesday: str
    Thursday: str
    Friday: str
    # Additional_Field_1: str
   

class ResultsByDays(BaseModel):
    description: ResultsByDaysDescription
    suggestion: str

class TradingDaysAnalysisDescription(BaseModel):
    Number_of_Days: str
    Avg_no_of_trades: str
    Positive_Days: str
    Avg_Positive_Day: str
    Negative_Days: str
    Avg_Negative_Day: str
    # Additional_Field_1: str

class TradingDaysAnalysis(BaseModel):
    description: TradingDaysAnalysisDescription
    suggestion: str

# class ResultsByInstrumentDescription(BaseModel):
#     description: str
#     # Additional_Field_1: str

class ResultsByInstrument(BaseModel):
    # description: ResultsByInstrumentDescription
    description: Dict[str, str]
    suggestion: str

class ResultsByPositionSizeDescription(BaseModel):
    Position_Size: str
    No_of_Trades: str
    Results: str
    High_Volume_Trades: str
    Profitable_Trades: str
    Losses: str
    Diversification: str
    # Additional_Field_1: str

class ResultsByPositionSize(BaseModel):
    description: ResultsByPositionSizeDescription
    suggestion: str

class ResultsByTradeDurationDescription(BaseModel):
    Duration: str
    No_of_Trades: str
    Results: str
    High_Frequency_Trading: str
    Profitable_Durations: str
    Losses_in_Longer_Durations: str
    One_Profitable_Trade: str
    # Additional_Field_1: str

class ResultsByTradeDuration(BaseModel):
    description: ResultsByTradeDurationDescription
    suggestion: str

class ResultsByOpenHourDescription(BaseModel):
    Hour: str
    No_of_Trades: str
    Results: str
    Peak_Trading_Hour: str
    Profitable_Hours: str
    Losses_During_Evening_Hours: str
    Mixed_Results: str
    # Additional_Field_1: str

class ResultsByOpenHour(BaseModel):
    description: ResultsByOpenHourDescription
    suggestion: str

class BodySchema(BaseModel):
    account_id: str
    long_short_comparison: LongShortComparison
    results_by_days: ResultsByDays
    trading_days_analysis: TradingDaysAnalysis
    results_by_instrument: ResultsByInstrument
    results_by_position_size: ResultsByPositionSize
    results_by_trade_duration: ResultsByTradeDuration
    results_by_open_hour: ResultsByOpenHour

'''
how to add to github 
git init 
add remote origin -- git add origin url of backend 
git clone 
git add  -- to add all the edited files 
git add . 

'''
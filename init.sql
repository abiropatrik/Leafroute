CREATE DATABASE IF NOT EXISTS DWH;
CREATE DATABASE IF NOT EXISTS STAGE;
CREATE DATABASE IF NOT EXISTS DM;
/* The following part can be ignored, since we are using django models
-- Drop STAGE tables
DROP TABLE IF EXISTS STAGE.Shipments, STAGE.Orders, STAGE.Vehicles, STAGE.Products, 
                    STAGE.WarehouseProducts, STAGE.Cities, STAGE.Warehouses, STAGE.WarehouseConnections, 
                    STAGE.Routes, STAGE.RouteParts, STAGE.Users, STAGE.WorkSchedules, STAGE.Addresses, 
                    STAGE.UserShipments;

-- Drop DWH tables
DROP TABLE IF EXISTS DWH.Shipments, DWH.Orders, DWH.Vehicles, DWH.Products, 
                    DWH.WarehouseProducts, DWH.Cities, DWH.Warehouses, DWH.WarehouseConnections, 
                    DWH.Routes, DWH.RouteParts, DWH.Users, DWH.WorkSchedules, DWH.Addresses, 
                    DWH.UserShipments;

-- STAGE TABLES 

CREATE TABLE STAGE.Vehicles (
    VehicleID  VARCHAR(255),
    Brand  VARCHAR(255),
    Model  VARCHAR(255),
    ProductionYear  VARCHAR(255),
    Type  VARCHAR(255),
    FuelType  VARCHAR(255),
    Consumption  VARCHAR(255),
    FullCapacity  VARCHAR(255),
    FreeCapacity  VARCHAR(255),
    Status  VARCHAR(255),
    AddressID  VARCHAR(255),
    AvgDistancePerHour  VARCHAR(255),
    FuelCost  VARCHAR(255)
);

CREATE TABLE STAGE.Orders(
    OrderID  VARCHAR(255),
    UserID  VARCHAR(255),
    ProductID  VARCHAR(255),
    WarehouseConnectionID  VARCHAR(255),
    RouteID  VARCHAR(255),
    Quantity  VARCHAR(255),
    OrderDate  VARCHAR(255),
    ExpectedFullfillmentDate  VARCHAR(255),
    FulfillmentDate  VARCHAR(255),
    OrderStatus  VARCHAR(255),
    ExpectedCO2Emission  VARCHAR(255),
    CO2Emmission  VARCHAR(255),
    Cost  VARCHAR(255)
);

CREATE TABLE STAGE.Shipments (
    ShipmentID  VARCHAR(255),
    OrderID  VARCHAR(255),
    VehicleID  VARCHAR(255),
    ProductID  VARCHAR(255),
    RoutePartsID  VARCHAR(255),
    ShipmentStartDate  VARCHAR(255),
    ShipmentEndDate  VARCHAR(255),
    Duration  VARCHAR(255),
    QuantityTransported  VARCHAR(255),
    FuelConsumed  VARCHAR(255),
    Status  VARCHAR(255),
    CO2Emission  VARCHAR(255),
    TransportCost  VARCHAR(255)
);

CREATE TABLE STAGE.Products (
ProductID  VARCHAR(255),
Name  VARCHAR(255),
Category  VARCHAR(255),
UnitPrice  VARCHAR(255),
Size  VARCHAR(255),
IsAlive  VARCHAR(255),
IsLiquid  VARCHAR(255),
IsHazardous  VARCHAR(255),
IsTimeSensitive  VARCHAR(255)
);

CREATE TABLE STAGE.WarehouseProducts (
PRODUCTID  VARCHAR(255),
WAREHOUSEID  VARCHAR(255),
FreeStock  VARCHAR(255),
ReservedStock  VARCHAR(255)
);

CREATE TABLE STAGE.Cities (
CityID  VARCHAR(255),
Country  VARCHAR(255),
Continent  VARCHAR(255),
Name  VARCHAR(255),
HasAirport  VARCHAR(255),
HasHarbour  VARCHAR(255),
LongitudeCoordinate  VARCHAR(255),
LatitudeCoordinate  VARCHAR(255)
);

CREATE TABLE STAGE.Warehouses (
WarehouseID  VARCHAR(255),
AddressID  VARCHAR(255),
Capacity  VARCHAR(255),
Fullness  VARCHAR(255),
ContactEmail  VARCHAR(255)
);

CREATE TABLE STAGE.WarehouseConnections (
WarehouseConnectionID  VARCHAR(255),
Warehouse1  VARCHAR(255),
Warehouse2  VARCHAR(255),
IsInDifferentCountry  VARCHAR(255),
IsInDifferentContinent  VARCHAR(255)
);

CREATE TABLE STAGE.Routes (
RouteID  VARCHAR(255),
WarehouseConnectionID  VARCHAR(255)
);

CREATE TABLE STAGE.RouteParts (
RoutePartID  VARCHAR(255),
RouteID  VARCHAR(255),
Distance  VARCHAR(255),
TransportMode  VARCHAR(255),
StartAddressID  VARCHAR(255),
EndAddressID  VARCHAR(255),
RouteCost  VARCHAR(255)
);

CREATE TABLE STAGE.Users (
UserID  VARCHAR(255),
Email  VARCHAR(255),
FirstName  VARCHAR(255),
LastName  VARCHAR(255),
AddressID  VARCHAR(255),
Job  VARCHAR(255),
Rights  VARCHAR(255),
HiringDate  VARCHAR(255),
CO2saved  VARCHAR(255),
Salary  VARCHAR(255)
);

CREATE TABLE STAGE.WorkSchedules (
Schedule_id  VARCHAR(255),
User_id  VARCHAR(255),
WorkDay  VARCHAR(255),
StartTime  VARCHAR(255),
EndTime  VARCHAR(255)
);

CREATE TABLE STAGE.Addresses (
AddressID  VARCHAR(255),
CityID  VARCHAR(255),
Street  VARCHAR(255),
HouseNumber  VARCHAR(255),
InstitutionName  VARCHAR(255)
);

CREATE TABLE STAGE.UserShipments (
UserID  VARCHAR(255),
ShipmentID  VARCHAR(255)
);


-- DWH TABLES

CREATE TABLE DWH.Vehicles (
    VehicleID  INT,
    Brand  VARCHAR(255),
    Model  VARCHAR(255),
    ProductionYear  INT,
    Type  VARCHAR(255),
    FuelType  VARCHAR(255),
    Consumption  FLOAT,
    FullCapacity  FLOAT,
    FreeCapacity  FLOAT,
    Status  VARCHAR(255),
    AddressID  INT,
    AvgDistancePerHour  FLOAT,
    FuelCost  FLOAT
);

CREATE TABLE DWH.Orders(
    OrderID  INT,
    UserID  INT,
    ProductID  INT,
    WarehouseConnectionID  INT,
    RouteID  INT,
    Quantity  INT,
    OrderDate  DATE,
    ExpectedFullfillmentDate  DATE,
    FulfillmentDate  DATE,
    OrderStatus  VARCHAR(255),
    ExpectedCO2Emission FLOAT,
    CO2Emmission  FLOAT,
    Cost  FLOAT
);

CREATE TABLE DWH.Shipments (
    ShipmentID  INT,
    OrderID  INT,
    VehicleID  INT,
    ProductID  INT,
    RoutePartsID  INT,
    ShipmentStartDate  DATETIME,
    ShipmentEndDate  DATETIME,
    Duration  INT,
    QuantityTransported  INT,
    FuelConsumed  FLOAT,
    Status  VARCHAR(255),
    CO2Emission  FLOAT,
    TransportCost  FLOAT
);

CREATE TABLE DWH.Products (
    ProductID  INT,
    Name  VARCHAR(255),
    Category  VARCHAR(255),
    UnitPrice  FLOAT,
    Size  FLOAT,
    IsAlive  BOOLEAN,
    IsLiquid  BOOLEAN,
    IsHazardous  BOOLEAN,
    IsTimeSensitive  BOOLEAN
);

CREATE TABLE DWH.WarehouseProducts (
    PRODUCTID  INT,
    WAREHOUSEID  INT,
    FreeStock  INT,
    ReservedStock  INT
);

CREATE TABLE DWH.Cities (
    CityID  INT,
    Country  VARCHAR(255),
    Continent  VARCHAR(255),
    Name  VARCHAR(255),
    HasAirport  BOOLEAN,
    HasHarbour  BOOLEAN,
    LongitudeCoordinate  FLOAT,
    LatitudeCoordinate  FLOAT
);

CREATE TABLE DWH.Warehouses (
    WarehouseID  INT,
    AddressID  INT,
    Capacity  INT,
    Fullness  INT,
    ContactEmail  VARCHAR(255)
);

CREATE TABLE DWH.WarehouseConnections (
    WarehouseConnectionID  INT,
    Warehouse1  INT,
    Warehouse2  INT,
    IsInDifferentCountry  BOOLEAN,
    IsInDifferentContinent  BOOLEAN
);

CREATE TABLE DWH.Routes (
    RouteID  INT,
    WarehouseConnectionID  INT
);

CREATE TABLE DWH.RouteParts (
    RoutePartID  INT,
    RouteID  INT,
    Distance  FLOAT,
    TransportMode  VARCHAR(255),
    StartAddressID  INT,
    EndAddressID  INT,
    RouteCost  FLOAT
);

CREATE TABLE DWH.Users (
    UserID  INT,
    Email  VARCHAR(255),
    FirstName  VARCHAR(255),
    LastName  VARCHAR(255),
    AddressID  INT,
    Job  VARCHAR(255),
    Rights  VARCHAR(255),
    HiringDate  DATE,
    CO2saved  FLOAT,
    Salary  FLOAT
);

CREATE TABLE DWH.WorkSchedules (
    Schedule_id  INT,
    User_id  INT,
    WorkDay  DATE,
    StartTime  TIME,
    EndTime  TIME
);

CREATE TABLE DWH.Addresses (
    AddressID  INT,
    CityID  INT,
    Street  VARCHAR(255),
    HouseNumber  VARCHAR(255),
    InstitutionName  VARCHAR(255)
);

CREATE TABLE DWH.UserShipments (
    UserID  INT,
    ShipmentID  INT
);
*/
SELECT 'init.sql executed' AS status;

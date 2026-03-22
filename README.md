# Dream Cars – FastAPI Car Rental Service

A RESTful car rental API built with **FastAPI** and **Python**. It supports managing a car fleet, creating rentals, applying discounts, and returning vehicles.

---

## Tech Stack

- **Python**
- **FastAPI**
- **Pydantic** (request validation)
- **Uvicorn** (ASGI server)

---

## Setup & Installation

```bash
# 1. Clone the repository
git clone https://github.com/K-P-Videsh-Kumaar/fastapi-car-rental-service.git
cd fastapi-car-rental-service

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.  
Interactive docs: `http://127.0.0.1:8000/docs`

---

## Pre-loaded Fleet

| ID | Model    | Brand          | Type      | Price/Day | Fuel     | Available |
|----|----------|----------------|-----------|-----------|----------|-----------|
| 1  | Swift    | Maruti Suzuki  | Hatchback | ₹1200     | Petrol   | Yes       |
| 2  | City     | Honda          | Sedan     | ₹2000     | Petrol   | No        |
| 3  | Creta    | Hyundai        | SUV       | ₹2500     | Diesel   | Yes       |
| 4  | Model 3  | Tesla          | Luxury    | ₹5000     | Electric | Yes       |
| 5  | Baleno   | Maruti Suzuki  | Hatchback | ₹1300     | Petrol   | No        |
| 6  | Fortuner | Toyota         | SUV       | ₹4000     | Diesel   | Yes       |

---

## Pricing Logic

| Rental Duration | Discount |
|-----------------|----------|
| 1 – 7 days      | No discount |
| 8 – 14 days     | 15% off base cost |
| 15 – 30 days    | 25% off base cost |

**Add-ons:**
- Insurance: **+₹500 / day**
- Driver: **+₹800 / day**

---

## Data Models

### NewCar (POST /cars)
| Field          | Type   | Constraints          |
|----------------|--------|----------------------|
| model          | string | min length: 2        |
| brand          | string | min length: 2        |
| price_per_day  | int    | > 0                  |
| type           | string | min length: 6        |
| fuel_type      | string | min length: 2        |
| is_available   | bool   | default: `true`      |

### RentalRequest (POST /rentals)
| Field           | Type   | Constraints             |
|-----------------|--------|-------------------------|
| customer_name   | string | min length: 2           |
| car_id          | int    | > 0                     |
| days            | int    | 1 – 30                  |
| license_number  | string | min length: 8           |
| insurance       | bool   | default: `false`        |
| driver_required | bool   | default: `false`        |

---

## API Endpoints

### Cars

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/cars` | List all cars with availability count |
| GET | `/cars/summary` | Fleet statistics (fuel types, car types, price range) |
| GET | `/cars/sort?by=` | Sort cars — valid values: `price_per_day`, `brand`, `type` |
| GET | `/cars/unavailable` | List all unavailable cars |
| GET | `/cars/page?page=&limit=` | Paginated car list (default: 3 per page) |
| GET | `/cars/filter` | Filter by `type`, `brand`, `fuel_type`, `max_price`, `is_available` |
| GET | `/cars/browse` | Advanced search with keyword, filters, sorting, and pagination |
| GET | `/cars/search/{keyword}` | Search cars by keyword (model, brand, or type) |
| GET | `/cars/{car_id}` | Get a single car by ID |
| POST | `/cars` | Add a new car |
| PUT | `/cars/{car_id}` | Update `price_per_day` and/or `is_available` via query params |
| DELETE | `/cars/{car_id}` | Delete a car (blocked if it has an active rental) |

#### `/cars/browse` Query Parameters
| Param | Type | Description |
|-------|------|-------------|
| `keyword` | string | Search across model, brand, type |
| `type` | string | Filter by car type |
| `fuel_type` | string | Filter by fuel type |
| `max_price` | int | Max price per day |
| `is_available` | bool | Filter by availability |
| `sort_by` | string | `price_per_day` (default), `brand`, `type`, `model` |
| `order` | string | `asc` (default) or `desc` |
| `page` | int | Page number (default: 1) |
| `limit` | int | Results per page (default: 10, max: 100) |

---

### Rentals

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/rentals` | List all rentals |
| GET | `/rentals/active` | List active rentals |
| GET | `/rentals/search?customer_name=` | Search rentals by customer name |
| GET | `/rentals/sort?by=` | Sort rentals — valid values: `total_cost`, `days` |
| GET | `/rentals/page?page=&size=` | Paginate rentals (default: 10 per page) |
| GET | `/rentals/by-car/{car_id}` | Get all rentals for a specific car |
| GET | `/rentals/{rental_id}` | Get a rental by ID |
| POST | `/rentals` | Create a new rental (marks the car as unavailable) |
| POST | `/return/{rental_id}` | Return a rented car (marks it as available again) |

---

## Example Requests

**Create a rental:**
```http
POST /rentals
Content-Type: application/json

{
  "customer_name": "Arun Kumar",
  "car_id": 3,
  "days": 10,
  "license_number": "TN01AB1234",
  "insurance": true,
  "driver_required": false
}
```

**Add a new car:**
```http
POST /cars
Content-Type: application/json

{
  "model": "Nexon",
  "brand": "Tata",
  "price_per_day": 2200,
  "type": "SUV",
  "fuel_type": "Petrol",
  "is_available": true
}
```

**Return a car:**
```http
POST /return/1
```

---

## Notes

- Data is stored **in-memory**; all data resets when the server restarts.
- A car cannot be deleted while it has an **active rental**.
- Rental duration is capped at **30 days**.

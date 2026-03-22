from fastapi import FastAPI, Query, Response, status,HTTPException
from pydantic import BaseModel, Field

app=FastAPI()

class NewCar(BaseModel):
    model: str= Field(min_length=2)
    brand: str= Field(min_length=2)
    price_per_day : int = Field(gt=0)
    type: str =Field(min_length=6)
    fuel_type : str = Field(min_length=2)
    is_available: bool= True


class RentalRequest(BaseModel):
    customer_name: str = Field(min_length=2)
    car_id: int = Field(gt=0)
    days: int = Field(gt=0, le=30)
    license_number: str = Field(min_length=8)
    insurance: bool = False
    driver_required:bool=False

def findcar(carid):
    result=[c for c in cars if c['id']==carid]
    if not result:
        return None
    return result[0]

def calculate_rental_cost(price_per_day,days,insurance,driver_required):
    total = price_per_day * days
    if days>=15:
        total*=0.75
    elif days>=8:
        total*=0.85
    if insurance:
        total += 500 * days
    
    if driver_required:
        total+=800*days
    return total

def filter_cars_logic(car_type=None, brand=None, fuel_type=None, max_price=None, is_available=None):
    filtered_cars = []
    for car in cars:
        if car_type is not None and car['type'].lower() != car_type.lower():
            continue
        if brand is not None and car['brand'].lower() != brand.lower():
            continue
        if fuel_type is not None and car['fuel_type'].lower() != fuel_type.lower():
            continue
        if max_price is not None and car['price_per_day'] > max_price:
            continue
        if is_available is not None and car['is_available'] != is_available:
            continue
        
        filtered_cars.append(car)
    
    return filtered_cars


@app.get('/')
def welcome():
    return {"Welcome to Dream Cars, Car Rental Company.Happy to help you"}

@app.get('/cars')
def getcars():
    result=[c for c in cars if c['is_available']]
    return {'Cars available':cars,'Total cars':len(cars),'available_count':len(result)}

@app.get('/cars/summary')
def summary():
    max1 = cars[0]['price_per_day']
    min1 = cars[0]['price_per_day']
    name1 = cars[0]['model']
    name2 = cars[0]['model']
    l=[0,0,0]
    t=[0,0,0,0]
    for c in cars:
        if c['fuel_type'.lower()]=='diesel':
            l[0]+=1
        elif c['fuel_type'.lower()]=='petrol':
            l[1]+=1
        else:
            l[2]+=1
        if(c['price_per_day']>max1):
            max1=c['price_per_day']
            name1=c['model']
        elif(c['price_per_day']<min1):
            min1=c['price_per_day']
            name2=c['model']
        if c['type'].lower() == 'suv':
            t[0] += 1
        elif c['type'].lower() == 'hatchback':
            t[1] += 1
        elif c['type'].lower()=='sedan':
            t[2]+=1
        else:
            t[3] += 1
    return{
        'total_cars':len(cars),
        'available':len([c for c in cars if c['is_available']==True]),
        'Petrol cars':l[1],
        'Diesel cars':l[0],
        'Electric Cars':l[2],
        'Sedans Cars':t[2],
        'Hatchbacks Cars':t[1],
        'Suv Cars':t[0],
        'Luxury Cars':t[3],
        'most_expensive':{'model':name1,'price_per_day':max1},
        'cheapest':{'model':name2,'price_per_day':min1},
    }

@app.get('/cars/sort')
def sortby(by: str = Query('price_per_day')):
    sort_fields = ["price_per_day", "brand", "type"]
    if by.lower() not in sort_fields:
        raise HTTPException(status_code=400, detail="Invalid Column")
    sorted_cars = sorted(cars, key=lambda x: x[by.lower()])
    return {"sorted_cars": sorted_cars}

@app.get('/cars/unavailable')
def get_unavailable_cars():
    unavailable_cars = [c for c in cars if not c.get('is_available', True)]
    return {
        "unavailable_cars": unavailable_cars,
        "count": len(unavailable_cars)
    }

@app.get('/cars/page')
def filter_page(
    page:int = Query(1),
    limit:int = Query(3)):
    start = (page - 1) * limit
    end   = start + limit
    paged = cars[start:end]
    return {
        'page':page,
        'limit':limit,
        'total':len(cars),
        'total_pages': -(-len(cars) // limit),  
        'cars':    paged,
    }

@app.get('/cars/browse')
def browse_cars(
    keyword: str = Query(None),
    type: str = Query(None),
    fuel_type: str = Query(None),
    max_price: int = Query(None),
    is_available: bool = Query(None),
    sort_by: str = Query('price_per_day'),
    order: str = Query('asc'),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    # Start with all cars
    filtered_cars = cars.copy()
    
    # Apply filters in order
    if keyword:
        filtered_cars = [
            car for car in filtered_cars
            if keyword.lower() in car.get('model', '').lower() or 
               keyword.lower() in car.get('brand', '').lower() or 
               keyword.lower() in car.get('type', '').lower()
        ]
    
    if type:
        filtered_cars = [
            car for car in filtered_cars
            if car.get('type', '').lower() == type.lower()
        ]
    
    if fuel_type:
        filtered_cars = [
            car for car in filtered_cars
            if car.get('fuel_type', '').lower() == fuel_type.lower()
        ]
    
    if max_price is not None:
        filtered_cars = [
            car for car in filtered_cars
            if car.get('price_per_day', 0) <= max_price
        ]
    
    if is_available is not None:
        filtered_cars = [
            car for car in filtered_cars
            if car.get('is_available', True) == is_available
        ]
    
    # Apply sorting
    valid_sort_fields = ['price_per_day', 'brand', 'type', 'model']
    if sort_by.lower() not in valid_sort_fields:
        raise HTTPException(status_code=400, detail="Invalid sort field")
    
    reverse_order = order.lower() == 'desc'
    sorted_cars = sorted(filtered_cars, key=lambda x: x.get(sort_by.lower(), ''), reverse=reverse_order)
    
    # Apply pagination
    start_index = (page - 1) * limit
    end_index = start_index + limit
    paginated_cars = sorted_cars[start_index:end_index]
    
    return {
        "metadata": {
            "filters_applied": {
                "keyword": keyword,
                "type": type,
                "fuel_type": fuel_type,
                "max_price": max_price,
                "is_available": is_available
            },
            "sorting": {
                "sort_by": sort_by,
                "order": order
            },
            "pagination": {
                "page": page,
                "limit": limit,
                "total_results": len(sorted_cars),
                "total_pages": (len(sorted_cars) + limit - 1) // limit,
                "has_next": end_index < len(sorted_cars),
                "has_previous": page > 1
            }
        },
        "results": paginated_cars,
        "count": len(paginated_cars)
    }

@app.get('/cars/filter')
def filter_cars(
    type: str = Query(None),
    brand: str = Query(None),
    fuel_type: str = Query(None),
    max_price: int = Query(None),
    is_available: bool = Query(None)
):
    filtered_cars = filter_cars_logic(type, brand, fuel_type, max_price, is_available)
    return {
        "filtered_cars": filtered_cars,
        "count": len(filtered_cars),
        "filters_applied": {
            "type": type,
            "brand": brand,
            "fuel_type": fuel_type,
            "max_price": max_price,
            "is_available": is_available
        }
    }

@app.get('/cars/search/{keyword}')
def search(keyword:str):
    total_found=0
    matches=[]
    for car in cars:
        if keyword.lower() in car['model'].lower() or keyword.lower() in car['brand'].lower() or keyword.lower() in car['type'].lower():
            matches.append(car)
            total_found+=1
    return {
        'matches':matches,
        'total_found':total_found
    }

@app.get('/cars/{car_id}')
def get_car(car_id:int):
    result=[c for c in cars if c['id']==car_id]
    if result is None:
        return {"error no cars found"}
    return{'car':result}

@app.get("/rentals")
def get_rentals():
    return {
        "total": len(rentals),
        "rentals": rentals
    }

@app.get('/rentals/active')
def get_active_rentals():
    active_rentals = [r for r in rentals if r.get('status') == 'active']
    return {
        "active_rentals": active_rentals,
        "count": len(active_rentals)
    }

@app.get('/rentals/search')
def search_rentals(customer_name: str = Query(...)):
    search_results = []
    for rental in rentals:
        if customer_name.lower() in rental.get('customer_name', '').lower():
            search_results.append(rental)
    
    return {
        "search_term": customer_name,
        "results": search_results,
        "count": len(search_results)
    }

@app.get('/rentals/sort')
def sort_rentals(by: str = Query('total_cost')):
    sort_fields = ["total_cost", "days"]
    if by.lower() not in sort_fields:
        raise HTTPException(status_code=400, detail="Invalid sort field")
    
    sorted_rentals = sorted(rentals, key=lambda x: x.get('cost_breakdown', {}).get(by.lower(), 0))
    return {
        "sorted_by": by,
        "rentals": sorted_rentals,
        "count": len(sorted_rentals)
    }

@app.get('/rentals/page')
def paginate_rentals(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)):
    start_index = (page - 1) * size
    end_index = start_index + size
    
    paginated_rentals = rentals[start_index:end_index]
    
    return {
        "page": page,
        "page_size": size,
        "total_rentals": len(rentals),
        "total_pages": (len(rentals) + size - 1) // size,
        "rentals": paginated_rentals,
        "has_next": end_index < len(rentals),
        "has_previous": page > 1
    }

@app.get('/rentals/by-car/{car_id}')
def get_rentals_by_car(car_id: int):
    car_rentals = [r for r in rentals if r.get('car_id') == car_id]
    return {
        "car_id": car_id,
        "rentals": car_rentals,
        "count": len(car_rentals)
    }

@app.get('/rentals/{rental_id}')
def get_rental(rental_id: int):
    for rental in rentals:
        if rental.get('rental_id') == rental_id:
            return rental
    raise HTTPException(status_code=404, detail="Rental not found")

@app.post('/cars')
def add_car(details:NewCar):
    for c in cars:
        if details.brand==c['brand'] and details.model==c['model']:
            raise HTTPException(status_code=400, detail="Car already exists")
    new_car = details.dict()
    new_car['id'] = max(car['id'] for car in cars) + 1 if cars else 1
    cars.append(new_car)
    
    return {
        "message": "Car added successfully",
        "car": new_car
    }

@app.post('/rentals')
def rental(data:RentalRequest):
    car = findcar(data.car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    if not car.get("is_available"):
        raise HTTPException(status_code=400, detail="Car not available")
    base_cost = car['price_per_day'] * data.days
    discount = 0
    if data.days >= 15:
        discount = base_cost * 0.25
    elif data.days >= 8:
        discount = base_cost * 0.15
    
    insurance_cost = 500 * data.days if data.insurance else 0
    driver_cost = 800 * data.days if data.driver_required else 0
    
    total_cost = calculate_rental_cost(car['price_per_day'], data.days, data.insurance, data.driver_required)
    rental = {
        "rental_id": max(rental.get('rental_id', 0) for rental in rentals) + 1 if rentals else 1,
        "customer_name": data.customer_name,
        "license_number": data.license_number,
        "car_id": data.car_id,
        "car_model": car["model"],
        "car_brand": car.get("brand"),
        "days": data.days,
        "insurance": data.insurance,
        "driver_required": data.driver_required,
        "cost_breakdown": {
            "base_cost": base_cost,
            "discount": discount,
            "insurance_cost": insurance_cost,
            "driver_cost": driver_cost,
            "total_cost": total_cost
        },
        "status": "active"
    }
    rentals.append(rental)
    return rental   

@app.post('/return/{rental_id}')
def return_car(rental_id: int):
    for rental in rentals:
        if rental.get('rental_id') == rental_id:
            if rental.get('status') == 'returned':
                raise HTTPException(status_code=400, detail="Car already returned")
            
            rental['status'] = 'returned'
            
            car = findcar(rental.get('car_id'))
            if car:
                car['is_available'] = True
            
            return {
                "message": "Car returned successfully",
                "rental": rental
            }
    
    raise HTTPException(status_code=404, detail="Rental not found")

@app.put('/cars/{car_id}')
def update_car(car_id: int, price_per_day: int = Query(None), is_available: bool = Query(None)):
    car = findcar(car_id)
    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    
    updated_fields = {}
    if price_per_day is not None:
        car['price_per_day'] = price_per_day
        updated_fields['price_per_day'] = price_per_day
    
    if is_available is not None:
        car['is_available'] = is_available
        updated_fields['is_available'] = is_available
    
    return {
        "message": "Car updated successfully",
        "car_id": car_id,
        "updated_fields": updated_fields,
        "updated_car": car
    }

@app.delete('/cars/{car_id}')
def delete_car(car_id: int):
    car = findcar(car_id)
    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    
    for rental in rentals:
        if rental.get('car_id') == car_id and rental.get('status') == 'active':
            raise HTTPException(status_code=400, detail="Car has active rental")
    
    cars.remove(car)
    return {
        "message": "Car deleted successfully",
        "deleted_car": car
    }
cars = [
    {
        "id": 1,
        "model": "Swift",
        "brand": "Maruti Suzuki",
        "type": "Hatchback",
        "price_per_day": 1200,
        "fuel_type": "Petrol",
        "is_available": True
    },
    {
        "id": 2,
        "model": "City",
        "brand": "Honda",
        "type": "Sedan",
        "price_per_day": 2000,
        "fuel_type": "Petrol",
        "is_available": False
    },
    {
        "id": 3,
        "model": "Creta",
        "brand": "Hyundai",
        "type": "SUV",
        "price_per_day": 2500,
        "fuel_type": "Diesel",
        "is_available": True
    },
    {
        "id": 4,
        "model": "Model 3",
        "brand": "Tesla",
        "type": "Luxury",
        "price_per_day": 5000,
        "fuel_type": "Electric",
        "is_available": True
    },
    {
        "id": 5,
        "model": "Baleno",
        "brand": "Maruti Suzuki",
        "type": "Hatchback",
        "price_per_day": 1300,
        "fuel_type": "Petrol",
        "is_available": False
    },
    {
        "id": 6,
        "model": "Fortuner",
        "brand": "Toyota",
        "type": "SUV",
        "price_per_day": 4000,
        "fuel_type": "Diesel",
        "is_available": True
    }
]

rentals=[]
rental_counter=1
@app.get('/cars')
def getcars():
    result=[c for c in cars if c['is_available']]
    return {'Cars available':cars,'Total cars':len(cars),'available_count':len(result)}


@app.get('/cars/summary')
def summary():
    max1 = cars[0]['price_per_day']
    min1 = cars[0]['price_per_day']
    name1 = cars[0]['model']
    name2 = cars[0]['model']
    l=[0,0,0]
    t=[0,0,0,0]
    for c in cars:
        if c['fuel_type'.lower()]=='diesel':
            l[0]+=1
        elif c['fuel_type'.lower()]=='petrol':
            l[1]+=1
        else:
            l[2]+=1
        if(c['price_per_day']>max1):
            max1=c['price_per_day']
            name1=c['model']
        elif(c['price_per_day']<min1):
            min1=c['price_per_day']
            name2=c['model']
        if c['type'].lower() == 'suv':
            t[0] += 1
        elif c['type'].lower() == 'hatchback':
            t[1] += 1
        elif c['type'].lower()=='sedan':
            t[2]+=1
        else:
            t[3] += 1
    return{
        'total_cars':len(cars),
        'available':len([c for c in cars if c['is_available']==True]),
        'Petrol cars':l[1],
        'Diesel cars':l[0],
        'Electric Cars':l[2],
        'Sedans Cars':t[2],
        'Hatchbacks Cars':t[1],
        'Suv Cars':t[0],
        'Luxury Cars':t[3],
        'most_expensive':{'model':name1,'price_per_day':max1},
        'cheapest':{'model':name2,'price_per_day':min1},
    }

@app.get('/cars/sort')
def sortby(by: str = Query('price_per_day')):
    sort_fields = ["price_per_day", "brand", "type"]
    if by.lower() not in sort_fields:
        raise HTTPException(status_code=400, detail="Invalid Column")
    sorted_cars = sorted(cars, key=lambda x: x[by.lower()])
    return {"sorted_cars": sorted_cars}
@app.get('/cars/unavailable')
def get_unavailable_cars():
    unavailable_cars = [c for c in cars if not c.get('is_available', True)]
    return {
        "unavailable_cars": unavailable_cars,
        "count": len(unavailable_cars)
    }
@app.get('/cars/page')
def filter_page(
    page:int = Query(1),
    limit:int = Query(3)):
    start = (page - 1) * limit
    end   = start + limit
    paged = cars[start:end]
    return {
        'page':page,
        'limit':limit,
        'total':len(cars),
        'total_pages': -(-len(cars) // limit),  
        'cars':    paged,
    }
    
@app.get('/cars/browse')
def browse_cars(
    keyword: str = Query(None),
    type: str = Query(None),
    fuel_type: str = Query(None),
    max_price: int = Query(None),
    is_available: bool = Query(None),
    sort_by: str = Query('price_per_day'),
    order: str = Query('asc'),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    filtered_cars = cars.copy()  
    if keyword:
        filtered_cars = [
            car for car in filtered_cars
            if keyword.lower() in car.get('model', '').lower() or 
               keyword.lower() in car.get('brand', '').lower() or 
               keyword.lower() in car.get('type', '').lower()
        ]
    if type:
        filtered_cars = [
            car for car in filtered_cars
            if car.get('type', '').lower() == type.lower()
        ]
    if fuel_type:
        filtered_cars = [
            car for car in filtered_cars
            if car.get('fuel_type', '').lower() == fuel_type.lower()
        ]
    if max_price is not None:
        filtered_cars = [
            car for car in filtered_cars
            if car.get('price_per_day', 0) <= max_price
        ]
    if is_available is not None:
        filtered_cars = [
            car for car in filtered_cars
            if car.get('is_available', True) == is_available
        ]
    valid_sort_fields = ['price_per_day', 'brand', 'type', 'model']
    if sort_by.lower() not in valid_sort_fields:
        raise HTTPException(status_code=400, detail="Invalid sort field")
    reverse_order = order.lower() == 'desc'
    sorted_cars = sorted(filtered_cars, key=lambda x: x.get(sort_by.lower(), ''), reverse=reverse_order)
    start_index = (page - 1) * limit
    end_index = start_index + limit
    paginated_cars = sorted_cars[start_index:end_index]
    return {
        "metadata": {
            "filters_applied": {
                "keyword": keyword,
                "type": type,
                "fuel_type": fuel_type,
                "max_price": max_price,
                "is_available": is_available
            },
            "sorting": {
                "sort_by": sort_by,
                "order": order
            },
            "pagination": {
                "page": page,
                "limit": limit,
                "total_results": len(sorted_cars),
                "total_pages": (len(sorted_cars) + limit - 1) // limit,
                "has_next": end_index < len(sorted_cars),
                "has_previous": page > 1
            }
        },
        "results": paginated_cars,
        "count": len(paginated_cars)
    }

@app.get('/cars/filter')
def filter_cars(
    type: str = Query(None),
    brand: str = Query(None),
    fuel_type: str = Query(None),
    max_price: int = Query(None),
    is_available: bool = Query(None)
):
    filtered_cars = filter_cars_logic(type, brand, fuel_type, max_price, is_available)
    return {
        "filtered_cars": filtered_cars,
        "count": len(filtered_cars),
        "filters_applied": {
            "type": type,
            "brand": brand,
            "fuel_type": fuel_type,
            "max_price": max_price,
            "is_available": is_available
        }
    }

@app.get('/cars/{car_id}')
def get_car(car_id:int):
    result=[c for c in cars if c['id']==car_id]
    if result is None:
        return {"error no cars found"}
    return{'car':result}

rentals=[]
rental_counter=1
@app.get("/rentals")
def get_rentals():
    return {
        "total": len(rentals),
        "rentals": rentals
    }
@app.get('/rentals/active')
def get_active_rentals():
    active_rentals = [r for r in rentals if r.get('status') == 'active']
    return {
        "active_rentals": active_rentals,
        "count": len(active_rentals)
    }

@app.get('/rentals/{rental_id}')
def get_rental(rental_id: int):
    for rental in rentals:
        if rental.get('rental_id') == rental_id:
            return rental
    raise HTTPException(status_code=404, detail="Rental not found")

@app.post('/return/{rental_id}')
def return_car(rental_id: int):
    for rental in rentals:
        if rental.get('rental_id') == rental_id:
            if rental.get('status') == 'returned':
                raise HTTPException(status_code=400, detail="Car already returned")
            
            rental['status'] = 'returned'
            
            car = findcar(rental.get('car_id'))
            if car:
                car['is_available'] = True
            
            return {
                "message": "Car returned successfully",
                "rental": rental
            }
    
    raise HTTPException(status_code=404, detail="Rental not found")

@app.post('/rentals')
def rental(data:RentalRequest):
    car = findcar(data.car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    if not car.get("is_available"):
        raise HTTPException(status_code=400, detail="Car not available")
    base_cost = car['price_per_day'] * data.days
    discount = 0
    if data.days >= 15:
        discount = base_cost * 0.25
    elif data.days >= 8:
        discount = base_cost * 0.15
    
    insurance_cost = 500 * data.days if data.insurance else 0
    driver_cost = 800 * data.days if data.driver_required else 0
    
    total_cost = calculate_rental_cost(car['price_per_day'], data.days, data.insurance, data.driver_required)
    rental = {
        "rental_id": max(rental.get('rental_id', 0) for rental in rentals) + 1 if rentals else 1,
        "customer_name": data.customer_name,
        "license_number": data.license_number,
        "car_id": data.car_id,
        "car_model": car["model"],
        "car_brand": car.get("brand"),
        "days": data.days,
        "insurance": data.insurance,
        "driver_required": data.driver_required,
        "cost_breakdown": {
            "base_cost": base_cost,
            "discount": discount,
            "insurance_cost": insurance_cost,
            "driver_cost": driver_cost,
            "total_cost": total_cost
        },
        "status": "active"
    }
    rentals.append(rental)
    return rental   

@app.post('/cars')
def add_car(details:NewCar):
    for c in cars:
        if details.brand==c['brand'] and details.model==c['model']:
            raise HTTPException(status_code=400, detail="Car already exists")
    new_car = details.dict()
    new_car['id'] = max(car['id'] for car in cars) + 1 if cars else 1
    cars.append(new_car)
    
    return {
        "message": "Car added successfully",
        "car": new_car
    }

@app.put('/cars/{car_id}')
def update_car(car_id: int, price_per_day: int = Query(None), is_available: bool = Query(None)):
    car = findcar(car_id)
    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    
    updated_fields = {}
    if price_per_day is not None:
        car['price_per_day'] = price_per_day
        updated_fields['price_per_day'] = price_per_day
    
    if is_available is not None:
        car['is_available'] = is_available
        updated_fields['is_available'] = is_available
    
    return {
        "message": "Car updated successfully",
        "car_id": car_id,
        "updated_fields": updated_fields,
        "updated_car": car
    }

@app.delete('/cars/{car_id}')
def delete_car(car_id: int):
    car = findcar(car_id)
    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    
    for rental in rentals:
        if rental.get('car_id') == car_id and rental.get('status') == 'active':
            raise HTTPException(status_code=400, detail="Car has active rental")
    
    cars.remove(car)
    return {
        "message": "Car deleted successfully",
        "deleted_car": car
    }
    
@app.get('/rentals/by-car/{car_id}')
def get_rentals_by_car(car_id: int):
    car_rentals = [r for r in rentals if r.get('car_id') == car_id]
    return {
        "car_id": car_id,
        "rentals": car_rentals,
        "count": len(car_rentals)
    }



@app.get('/rentals/search')
def search_rentals(customer_name: str = Query(...)):
    search_results = []
    for rental in rentals:
        if customer_name.lower() in rental.get('customer_name', '').lower():
            search_results.append(rental)
    
    return {
        "search_term": customer_name,
        "results": search_results,
        "count": len(search_results)
    }

@app.get('/rentals/sort')
def sort_rentals(by: str = Query('total_cost')):
    sort_fields = ["total_cost", "days"]
    if by.lower() not in sort_fields:
        raise HTTPException(status_code=400, detail="Invalid sort field")
    
    sorted_rentals = sorted(rentals, key=lambda x: x.get('cost_breakdown', {}).get(by.lower(), 0))
    return {
        "sorted_by": by,
        "rentals": sorted_rentals,
        "count": len(sorted_rentals)
    }

@app.get('/rentals/page')
def paginate_rentals(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)):
    start_index = (page - 1) * size
    end_index = start_index + size
    
    paginated_rentals = rentals[start_index:end_index]
    
    return {
        "page": page,
        "page_size": size,
        "total_rentals": len(rentals),
        "total_pages": (len(rentals) + size - 1) // size,
        "rentals": paginated_rentals,
        "has_next": end_index < len(rentals),
        "has_previous": page > 1
    }

@app.get('/cars/search/{keyword}')
def search(keyword:str ):
    total_found=0
    matches=[]
    for car in cars:
        if keyword.lower() in car['model'].lower() or keyword.lower() in car['brand'].lower() or keyword.lower() in car['type'].lower():
            matches.append(car)
            total_found+=1
    return {
        'matches':matches,
        'total_found':total_found
    }


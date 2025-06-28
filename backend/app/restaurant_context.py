import json
import os
from typing import Dict, Any

class RestaurantContext:
    """Loads and manages restaurant context from multiple JSON files."""
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.menu_data = self._load_json('menu.json')
        self.hours_data = self._load_json('hours.json')
        self.restaurant_info = self._load_json('restaurant_info.json')
        
    def _load_json(self, filename: str) -> Dict[str, Any]:
        """Load JSON file from data directory."""
        try:
            file_path = os.path.join(self.data_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Warning: {filename} not found in {self.data_dir}")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {filename}")
            return {}
    
    def get_full_context(self) -> str:
        """Generate complete restaurant context for the AI chatbot."""
        context = f"""
You are a helpful customer service chatbot for CAFICAFE restaurant. 

RESTAURANT INFORMATION:
- Name: {self.restaurant_info.get('basic_info', {}).get('name', 'CAFICAFE')}
- Tagline: {self.restaurant_info.get('basic_info', {}).get('tagline', '')}
- Description: {self.restaurant_info.get('basic_info', {}).get('description', '')}

LOCATION & CONTACT:
- Address: {self.restaurant_info.get('location', {}).get('address', '')}
- Phone: {self.restaurant_info.get('location', {}).get('phone', '')}
- Email: {self.restaurant_info.get('location', {}).get('email', '')}
- Directions: {self.restaurant_info.get('location', {}).get('directions', '')}

OPENING HOURS:
{self._format_hours()}

SIGNATURE DISHES:
{self._format_signature_dishes()}

RECOMMENDED DISHES:
{self._format_recommended_dishes()}

DIETARY ACCOMMODATIONS:
{self._format_dietary_info()}

BOOKING INFORMATION:
{self._format_booking_info()}

FEATURES:
{self._format_features()}

INSTRUCTIONS:
- Always be friendly, helpful, and professional
- Provide accurate information based on the context above
- If asked about something not covered, politely say you don't have that information and suggest contacting the restaurant directly
- For reservations, direct customers to call {self.restaurant_info.get('location', {}).get('phone', '')} or use the online system
- Mention student discounts when relevant
- Be welcoming to tourists and explain dishes clearly
- If someone asks about allergens or dietary restrictions, always recommend speaking with staff directly for safety
"""
        return context
    
    def _format_hours(self) -> str:
        """Format opening hours information."""
        hours = self.hours_data.get('regular_hours', {})
        formatted = []
        for day, time in hours.items():
            formatted.append(f"- {day.capitalize()}: {time}")
        
        special_notes = self.hours_data.get('special_notes', [])
        if special_notes:
            formatted.append("\nSpecial Notes:")
            for note in special_notes:
                formatted.append(f"- {note}")
                
        return "\n".join(formatted)
    
    def _format_signature_dishes(self) -> str:
        """Format signature dishes information."""
        dishes = self.menu_data.get('signature_dishes', [])
        formatted = []
        for dish in dishes:
            formatted.append(f"- {dish.get('name', '')}: {dish.get('description', '')} - {dish.get('price', '')}")
        return "\n".join(formatted)
    
    def _format_recommended_dishes(self) -> str:
        """Format recommended dishes information."""
        dishes = self.menu_data.get('recommended_dishes', [])
        formatted = []
        for dish in dishes:
            formatted.append(f"- {dish.get('name', '')}: {dish.get('description', '')} - {dish.get('price', '')}")
        return "\n".join(formatted)
    
    def _format_dietary_info(self) -> str:
        """Format dietary accommodation information."""
        accommodations = self.menu_data.get('dietary_accommodations', {})
        formatted = []
        for diet_type, info in accommodations.items():
            formatted.append(f"- {diet_type.replace('_', ' ').title()}: {info}")
        return "\n".join(formatted)
    
    def _format_booking_info(self) -> str:
        """Format booking information."""
        booking = self.restaurant_info.get('booking', {})
        methods = booking.get('methods', [])
        policies = booking.get('policies', [])
        
        formatted = ["Booking Methods:"]
        for method in methods:
            formatted.append(f"- {method}")
            
        if policies:
            formatted.append("\nPolicies:")
            for policy in policies:
                formatted.append(f"- {policy}")
                
        return "\n".join(formatted)
    
    def _format_features(self) -> str:
        """Format restaurant features."""
        features = self.restaurant_info.get('features', [])
        formatted = []
        for feature in features:
            formatted.append(f"- {feature}")
        return "\n".join(formatted)

# Global instance
restaurant_context = RestaurantContext()
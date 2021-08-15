#ifndef CIRCLE_H_
#define CIRCLE_H_

#include "shape.h"

/**
	A class that represents a circle on a
	2D plane. Its only member is its radius
	and it inherits all of its functionality from
	the Shape class.
	
	@author Brent Nash
*/
class Circle : public Shape
{
	private:
		
		/** The radius of the circle */
		int radius;
	
	public:
	
		/**
			Overloaded constructor that takes in a radius
			and an (x,y) coordinate.
			
			@param r The radius of the circle (must be greater than 0)
			@param x The X coordinate of the circle's center point in 2D space
			@param y The Y coordinate of the circle's center point in 2D space
		*/
		Circle(int r,int x,int y);
		
		/**
			Overloaded constructor that takes in a radius
			and a center Point.
			
			@param r The radius of the circle (must be greater than 0)
			@param c The center point of the circle in 2D space
		*/
		Circle(int r,Point c);
		
		/**
			Virtual function overridden from Shape. Returns a string
			indicating what type of shape this object is.
			@pre None
			@post Does not change the object
			@return The string "Circle"
		*/
		virtual std::string getType() const;
		
		/**
			Virtual function overridden from Shape. Returns the area
			of the circle as PI*radius*radius.
			
			@pre The radius must be set to a valid number.
			@post Does not change the object
			@return The area of the circle as a floating point number.
		*/
		virtual double getArea() const;
};

#endif
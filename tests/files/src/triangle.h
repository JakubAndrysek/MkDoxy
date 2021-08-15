#ifndef TRIANGLE_H_
#define TRIANGLE_H_

#include "shape.h"

/**
	A class that represents a triangle on a
	2D plane. Its only members are its base and height.
	It inherits all of its functionality from
	the Shape class.
	
	@author Brent Nash
*/
class Triangle : public Shape
{
	private:
		/** The base of the triangle */
		int base;
		/** The height of the triangle */
		int height;
	
	public:
	
		/**
			Overloaded constructor that takes in a base, a height
			and an (x,y) coordinate.
			
			@param b The base of the triangle (must be greater than 0)
			@param h The height of the triangle (must be greater than 0)
			@param x The X coordinate of the triangle's center point in 2D space
			@param y The Y coordinate of the triangle's center point in 2D space
		*/
		Triangle(int b,int h,int x,int y);
		
		/**
			Overloaded constructor that takes in a base, a height,
			and a center Point.
			
			@param b The base of the triangle (must be greater than 0)
			@param h The height of the triangle (must be greater than 0)
			@param c The center point of the triangle in 2D space
		*/
		Triangle(int b,int h,Point c);
		
		/**
			Virtual function overridden from Shape. Returns a string
			indicating what type of shape this object is.
			@pre None
			@post Does not change the object
			@return The string "Triangle"
		*/
		virtual std::string getType() const;
		
		/**
			Virtual function overridden from Shape. Returns the area
			of the triangle as (1/2)*base*height.
			
			@pre The base and height must be set to valid numbers.
			@post Does not change the object
			@return The area of the circle as a floating point number.
		*/
		virtual double getArea() const;
};

#endif
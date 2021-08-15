#ifndef RECTANGLE_H_
#define RECTANGLE_H_

#include "shape.h"

/**
	A class that represents a rectangle on a
	2D plane. Its only members are its length and width.
	It inherits all of its functionality from
	the Shape class.
	
	@author Brent Nash
*/
class Rectangle : public Shape
{
	private:
		/** The length of the rectangle */
		int length;
		/** The width of the rectangle */
		int width;
	
	public:
		
		/**
			Overloaded constructor that takes in a length, a width,
			and an (x,y) coordinate.
			
			@param l The length of the rectangle (must be greater than 0)
			@param w The width of the rectangle (must be greater than 0)
			@param x The X coordinate of the rectangle's center point in 2D space
			@param y The Y coordinate of the rectangle's center point in 2D space
		*/
		Rectangle(int l,int w,int x,int y);
		
		/**
			Overloaded constructor that takes in a length, a width,
			and a center Point.
			
			@param l The length of the rectangle (must be greater than 0)
			@param w The width of the rectangle (must be greater than 0)
			@param c The center point of the rectangle in 2D space
		*/
		Rectangle(int l,int w,Point c);
		
		/**
			Virtual function overridden from Shape. Returns a string
			indicating what type of shape this object is.
			@pre None
			@post Does not change the object
			@return The string "Rectangle"
		*/
		virtual std::string getType() const;
		
		/**
			Virtual function overridden from Shape. Returns the area
			of the rectangle as length*width.
			
			@pre The length and width must be set to valid numbers.
			@post Does not change the object
			@return The area of the rectangle as a floating point number.
		*/
		virtual double getArea() const;
};

#endif
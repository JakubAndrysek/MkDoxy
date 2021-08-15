#ifndef SHAPE_H_
#define SHAPE_H_

#include <iostream>
#include "point.h"

/**
	An abstract base class that represents a shape on a
	2D plane. Its only member is "center" which maintains the
	center point of the shape. It has pure virtual methods for
	identifying the type of shape and calculating the shape's area
	that must be implemented by subclasses.
	
	@author Brent Nash
*/
class Shape
{
	protected:
		
		/** The center point of the shape as a 2D coordinate */
		Point center;
	
	public:
		
		/**
			Overloaded constructor that takes in an (x,y) coordinate.
			
			@param x The X coordinate of the shape's center point in 2D space
			@param y The Y coordinate of the shape's center point in 2D space
		*/
		Shape(int x,int y);
		
		/**
			Overloaded constructor that takes in a center Point.
			
			@param c The center point of the shape in 2D space
		*/
		Shape(Point c);
		
		/**
			Accessor for the shape's center point.
			
			@pre None
			@post Does not change the object
			@return The current center point of the shape as a Point object.
		*/
		Point getCenter() const;
		
		/**
			Mutator for the shape's center point.
			
			@pre None
			@post The "center" member variable of Shape will be changed to the input value.
			@param c The new center point for the Shape.
		*/
		void setCenter(Point c);
		
		/**
			Pure virtual function for Shape subclasses. Returns a string
			indicating what type of shape this object is.
			@pre None
			@post Does not change the object
			@return A string name of the current shape
		*/
		virtual std::string getType() const = 0;
		
		/**
			Pure virtual function for Shape subclasses. Subclasses overriding this
			method should use it to calculate the area of the shape and return the
			area as a floating point number.
			@pre Valid data must be set on the Shape object
			@post Does not change the object
			@return A floating point number representing the area of the Shape
		*/
		virtual double getArea() const = 0;
};

#endif
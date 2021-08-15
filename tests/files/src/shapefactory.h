#ifndef SHAPEFACTORY_H_
#define SHAPEFACTORY_H_

#include "shape.h"
#include <string>

/**
	A factory class to generate Shapes with randomly
	generated sizes/dimensions.

	@author Brent Nash
*/
class RandomSizeShapeFactory
{
	private:
		/**
			Default constructor.  Private so no one can ever
			instantiate this class.
		*/
		RandomSizeShapeFactory();
		
	public:
		/**
			Static factory method for creating shapes. Takes in a string
			representation of a shape and returns a pointer to that particular shape.
			Only works for shapes that derive from the Shape object. Center points for
			returned shapes will always be (0,0).
			
			@pre None
			@post Does not change the object
			@param name The name of the shape to generate (e.g. "triangle", "rectangle", or
			"circle"). Input is case-sensitive.
			@return A pointer to a Shape object dynamically allocated on the heap if "name" is
			a valid, recognized shape type or NULL if "name" does not specify the name of a known
			shape.
		*/
		static Shape* createShape(std::string name);
};

#endif
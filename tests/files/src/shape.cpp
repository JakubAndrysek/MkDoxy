#include "shape.h"

using namespace std;

//Overloaded constructor to set the center point as (x,y)
Shape::Shape(int x,int y)
: center(x,y)
{
	//empty
}

//Overloaded constructor to set the center point
Shape::Shape(Point c)
: center(c)
{
	//empty
}
		
//Accessor function for the center point
Point Shape::getCenter() const
{ 
	return center;
}

//Mutator function for the center point
void Shape::setCenter(Point c)
{ 
	center = c; 
}

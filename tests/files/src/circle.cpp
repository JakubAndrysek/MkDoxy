#include <cmath> //include for access to "pow"
#include "circle.h"

using namespace std;

//Overloaded circle constructor for radius and center point as (x,y)
Circle::Circle(int r,int x,int y) 
: Shape(x,y), radius(r)
{
	//empty
}

//Overloaded circle constructor for radius & center point
Circle::Circle(int r,Point c) 
: Shape(c), radius(r)
{
	//empty
}
		
//Method to return an identifier for the type of shape		
string Circle::getType() const
{
	return "Circle";
}

//Method to calculate the area of the circle as pi*r^2
double Circle::getArea() const
{
	return 3.1415 * pow((double)radius,(double)2);
}
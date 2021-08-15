#include "rectangle.h"

using namespace std;

//Overloaded constructor for length, width and center point as (x,y)
Rectangle::Rectangle(int l,int w,int x,int y) 
: Shape(x,y), length(l), width(w)
{
	//empty
}

//Overloaded constructor for length, width and center point
Rectangle::Rectangle(int l,int w,Point c)
: Shape(c), length(l), width(w)
{
	//empty
}

//Method to return an identifier for the type of shape		
string Rectangle::getType() const
{
	return "Rectangle";
}

//Method to calculate the area of the rectangle
double Rectangle::getArea() const
{
	return length * width;
}
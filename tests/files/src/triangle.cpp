#include "triangle.h"

using namespace std;

//Overloaded Triangle constructor for base, height and (x,y) as center point
Triangle::Triangle(int b,int h,int x,int y) 
: Shape(x,y), base(b), height(h)
{
	//empty
}

//Overloaded Triangle constructor for base/height/center_point
Triangle::Triangle(int b,int h,Point c) 
: Shape(c), base(b), height(h)
{
	//empty
}

//Method to return an identifier for the type of shape		
string Triangle::getType() const
{
	return "Triangle";
}

//Method to calculate the area of the triangle
double Triangle::getArea() const
{
	return .5*base*height;
}
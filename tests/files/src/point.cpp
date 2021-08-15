#include "point.h"

using namespace std;

//Default constructor that initializes point to (0,0)
Point::Point()
{ 
	x=0;
	y=0;
}

//Overloaded constructor for setting x and y
Point::Point(int newx,int newy)
{ 
	x=newx; 
	y=newy;
}

//Accessor for X
int Point::getX() const
{
	return x;
}

//Accessor for Y
int Point::getY() const
{ 
	return y; 
}

//Mutator for X
void Point::setX(int newx) 
{ 
	x=newx;
}

//Mutator for Y
void Point::setY(int newy)
{ 
	y=newy;
}

//Overloaded += operator to add a Point to this one
void Point::operator+=(const Point &right)
{
	this->x = this->x + right.getX();
	this->y = this->y + right.getY();
}

//Overloaded = operator to set this point equal to another one
Point& Point::operator=(const Point &other)
{
	//If the input Point is the same as the point
	//we're already inside of, there's nothing to do here
	if(this == &other)
	{
		return *this;
	}
	
	this->x = other.x;
	this->y = other.y;
	
	//return a reference to "this" for chaining
	return *this;
}

//Overloaded - for negation operations
Point operator-(const Point &a)
{
	Point c;
	c.x = -a.x;
	c.y = -a.y;
	return c;
}

//Overloaded == operator for comparing two points for equality
bool operator==(const Point &a,const Point &b)
{
	return a.x==b.x && a.y == b.y;
}

//Overloaded != operator for comparing two points for inequality
bool operator!=(const Point &a,const Point &b)
{
	//Call the existing overloaded == operator
	return !(a == b);
}

//Overloaded << operator for sending a Point to an output stream
ostream& operator<<(ostream& out,const Point &pt)
{
	//print out the Point as "(x,y)"
	out << "(" << pt.x << "," << pt.y << ")";
	return out;
}

//Overloaded >> operator for extracting a Point from a stream
istream& operator>>(istream& in, Point &pt)
{
	in >> pt.x;
	in >> pt.y;
	return in;
}

//Overloaded + operator for adding two points together
Point operator+(const Point &a,const Point &b)
{
	Point c;
	c.x = a.x + b.x;
	c.y = a.y + b.y;
	return(c);
}

//Overloaded + operator for a adding a point and an integer
Point operator+(const Point &a,const int &b)
{
	Point c;
	c.x = a.x + b;
	c.y = a.y + b;
	return c;
}
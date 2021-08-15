#ifndef POINT_H_
#define POINT_H_

#include <iostream>

/**
	A basic class to represent a point somewhere in
	2D space.

	@author Brent Nash
*/
class Point
{
	private:
		
		/** The X coordinate in 2D space */
		int x;
		/** The Y coordinate in 2D space */
		int y;
		
	public:
		
		/**
			Default constructor
			
			@post The X and Y coordinates are initialized to zero
		*/
		Point();
		
		/**
			Overloaded constructor
			
			@param newx The initial value for the X coordinate
			@param newy The initial value for the Y coordinate
		*/
		Point(int newx,int newy);
		
		/**
			Accessor for the X coordinate
			
			@pre None
			@post This method does not change the object
			@return The integer X coordinate
		*/
		int getX() const;
		
		/**
			Accessor for the Y coordinate
			
			@pre None
			@post This method does not change the object
			@return The integer Y coordinate
		*/
		int getY() const;
		
		/**
			Mutator for the X coordinate
			
			@pre None
			@post The X coordinate will be updated to the value of "newx"
			@param newx The new value for the X coordinate
		*/
		void setX(int newx);
		
		/**
			Mutator for the Y coordinate
			
			@pre None
			@post The Y coordinate will be updated to the value of "newy"
			@param newy The new value for the Y coordinate
		*/
		void setY(int newy);
		
		/**
			Overloaded + operator for adding two points together. Not a member
			function, but declared as a friend so it can access member variables. This
			implements:
			
			Point a, b;
			Point c = a + b;
			
			@pre None
			@post Does not change the current object
			@param a The point on the left side of the + sign (passed by const reference)
			@param b The point on the right side of the + sign (passed by const reference)
			@return A new point object created by adding together the individual coordinates
			from a & b (e.g. a.x + b.x, a.y + b.y, etc.)
		*/
		friend Point operator+(const Point &a,const Point &b);
		
		/**
			Overloaded + operator for adding an integer to a point. Not a member
			function, but declared as a friend so it can access member variables. This
			implements:
			
			Point a;
			int x;
			Point c = a + x;
			
			@pre None
			@post Does not change the current object
			@param a The point on the left side of the + sign (passed by const reference)
			@param b The int on the right side of the + sign (passed by const reference)
			@return A new point object created by adding b to each of the coordinates 
			of a (e.g. a.x + b, a.y + b, etc.)
		*/
		friend Point operator+(const Point &a,const int &b);
		
		/**
			Overloaded << operator for inserting a point in an output stream. Not a member
			function, but declared as a friend so it can access member variables. This
			implements:
			
			Point a;
			cout << a;
			
			Outputs a Point in the form "(x,y)" (no quotes)
			
			@pre None
			@post The ostream "out" will have "pt" inserted into it
			@param out The output stream being modified (passed by reference...will be changed!)
			@param pt The point being inserted into the output stream (passed by const reference)
			@return A reference to the input parameter "out" so that we can chain multiple <<
			operators together.
		*/
		friend std::ostream& operator<<(std::ostream& out,const Point &pt);
		
		/**
			Overloaded >> operator for extracting a point from an input stream. Not a member
			function, but declared as a friend so it can access member variables. This
			implements:
			
			Point a;
			cin >> a;
			
			Expects a Point to be entered in the form "X Y" (no quotes).
			
			@pre None
			@post The point "a" will be changed by whatever information was extracting from the istream
			@param in The input stream being modified (passed by reference...will be changed!)
			@param pt The point having input stream information extracted into it
			(passed by reference...will be changed!)
			@return A reference to the input parameter "in" so that we can chain multiple >>
			operators together.
		*/
		friend std::istream& operator>>(std::istream& in, Point &pt);
		
		/**
			Overloaded operator to compare two Points for equality.  Two points are equal if each
			of their individual member coordinates are equal.  Not a member function, but declared
			as a friend so it can access member variables.  This implements:
			
			Point a, b;
			if(a == b)
			
			@pre None
			@post No changes
			@param a The Point on the left side of the == operation (passed by const reference)
			@param b The Point on the right side of the == operation (passed by const reference)
			@return A bool value of "true" if the Points are equal. False otherwise.
		*/
		friend bool operator==(const Point &a,const Point &b);
		
		/**
			Overloaded operator to compare two Points for inequality.  Two points are not equal if any
			of their individual member coordinates are different.  Not a member function, but declared
			as a friend so it can access member variables.  This implements:
			
			Point a, b;
			if(a != b)
			
			@pre None
			@post No changes
			@param a The Point on the left side of the != operation (passed by const reference)
			@param b The Point on the right side of the != operation (passed by const reference)
			@return A bool value of "true" if the Points are not equal. False otherwise.
		*/
		friend bool operator!=(const Point &a,const Point &b);
		
		/**
			Overloaded unary operator negation operator to multiply each coordinate of the input Point
			by -1.  Not a member function, but declared
			as a friend so it can access member variables.  This implements:
			
			Point a, b;
			a = -b;
			
			@pre None
			@post No changes
			@param a The Point on the right side of the - operation (passed by const reference)
			@return A point whose values are the negation of the values in the input Point a 
			(e.g. if (5,6) is input, then (-5,-6) should be returned).
		*/
		friend Point operator-(const Point &a);
		
		/**
			Overloaded = operator used to set two Points equal to each other. Declared as a 
			member function because it changes the current object.  This implements:
			
			Point a, b;
			a = b;
			
			@pre None
			@post The values stored inside "this" will be changed to the values stored
			inside of "other"
			@param other The Point whose values should be copied into this Point
			(passed by const reference)
			@return A reference to "this" so that we can chain '=' operations together.
		*/
		Point& operator=(const Point &other);
		
		/**
			Overloaded += opreator used to increment the values in the current point by the
			coordinate values in another point.  This will take each of the coordinates in
			"right" and add them to each of the coordinates in "this" respectively. This 
			implements:
			
			Point a, b;
			a += b;
			
			@pre None
			@post The values in "this" will have been incremented by the values in "right"
			@param right The Point whose coordinates should be added to the coordinates of
			this Point (passed by const reference).
		*/
		void operator+=(const Point &right);
};

#endif
/** @mainpage CSCI 102 Lecture #9 Factory Class Example
 
@section purpose Purpose/Overview

The purpose of this program is to demonstrate the power and flexibility of 
a factory class.  The user will input names of shapes from the console and
behind the scenes a factory will instantiate and return randomly sized shapes
based on the input from the user.  When the user finishes entering shapes, the
program will also use polymorphism to print out the type and area of each
shape that was created.

@section reqs Requirements

The application shall accepts names of shapes from the user via the console.

The application shall gracefully report and handle invalid shape names without crashing.

The application shall use user input shape names to generate corresponding shape objects
via a factory class.

The application shall provide a way for the user to indicate they are done entering shapes.

The application, upon normal exit, shall display a summary to the user of all the shapes
that were created and their areas.

@section globals Global Data/Functions

There is no global data in this application.  All the data is contained within objects.

@section objects Objects

See the individual object documentation pages for more info on each object.

Point - A class representing a 2D (x,y) point in space.
Shape - An abstract base class used to represent a Shape.
Triangle - A class to represent a triangle shape in space. Inherits from Shape.
Rectangle - A class to represent a rectangle shape in space. Inherits from Shape.
Circle - A class to represent a circle shape in space. Inherits from Shape.
ShapeFactory - A factory class used for generating Shape pointers from strings.

@section arch High-level architecture

The main method of the program reads user input strings and passes them to the ShapeFactory object.
The ShapeFactory object is responsible for knowing how to create Shapes from strings and it will
return Shape pointers.  Triangle, Rectangle and Circle are only ever reference inside the ShapeFactory.
Everywhere else the abstract Shape interface is used to pass around data and polymorphically call
functions on the individual shapes.  Each Shape contains a Point object that represents its physical
location in 2D space (its center point).

The main flow of the code is:

1.  Prompt the user for a string
2.  Pass the string to the ShapeFactory to create a Shape*
3a.  If the shape string is bad, do nothing and reprompt the user.  Go to 2.
3b.  If the shape string is good, add the created shape to a vector. Go to 2.
3c.  If the input string is empty, end the program and dump a summary of created shapes.

@section functions Function Descriptions

All functions are described in detail on the documentation pages for the classes
that either contain them or are friends of them.

@section ui User Interface

The only user interface is that the user will be prompted to enter string representations
of shapes (e.g. "triangle") and the application will handling all the heavy lifting of creating
randomly sized shapes.  If the user enters a bad shape, they will be reprompted.  If the user enters
nothing, the program will end and dump a summary.

@section testing Testing

Test the main code with all the known existing shape types (Triangle, Circle, Rectangle) and make sure
that it works.  Also try entering the same shape multiple times (e.g. make 3 Circles).

Test that the main code handles bad shape names gracefully.  If a user enters a string like
"asdfsda" that is not a known shape, check that the application displays an error and reprompts.

Test that when the user enters an empty string, the program prints a summary and terminates.
 */

#include <iostream>
#include <string>
#include <vector>
#include <stdexcept>

#include "shape.h"
#include "shapefactory.h"

using namespace std;

/**
	Main method
	
	Prompt the user to enter names of shapes.  For each valid shape
	the user enters, create a randomly sized version of that shape and 
	put it in our list of shapes.  When the user is done (they enter
	nothing), print out all the shapes and their areas.
	
	@return The exit status of the program as an integer
*/
int main()
{
	//create a list of pointers to shapes...the user will populate
	//this with their console input
	vector<Shape*> shapes;
	
	string input;
	while(true)
	{
		//Read the shape from the user
		cout << "Enter a shape (empty string to quit): ";
		getline(cin,input);
		
		//if the user entered no text, we're done
		if(input.size() == 0)
		{
			cout << "Done entering shapes." << endl << endl;
			break;
		}
		
		//create the shape the user requested via the factory
		//(and check if it's a good value)
		Shape *s = RandomSizeShapeFactory::createShape(input);
		if(s == NULL)
		{
			cerr << "Hey! That's not a shape!" << endl;
			continue;
		}
		
		//add the shape to our list
		shapes.push_back(s);
	}
	
	//print out all the shape types and their areas to the console
	for(int i=0; i < shapes.size(); i++)
	{
		Shape *shape = shapes.at(i); //shapes[i]
		cout << "Shape " << shape->getType()
		     << " has area of " << shape->getArea() << endl;
	}
	
	return 0;
}

/*!
 * @example myExample.cpp
 * @brief This is an example
 * @details This is detailed docummentation
 */
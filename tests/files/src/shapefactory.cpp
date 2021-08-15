#include "shapefactory.h"
#include "shape.h"
#include "rectangle.h"
#include "circle.h"
#include "triangle.h"
#include <cstdlib>
#include <time.h>

using namespace std;

//Function to generate a random integer between 1 & 100
//
//NOTE: Since we only declare this function in the .cpp file
//and not in the .h file, it is hidden from everyone except
//functions defined in this file
int getRandomNumber()
{
	//get the system time
	time_t seconds;
	time(&seconds);
	
	//seed the random number generator with the time
	srand((unsigned int) seconds);
	
	//Get a random # between 1 & 100
	return rand()%100 + 1;
}

//Default constructor (does nothing)
RandomSizeShapeFactory::RandomSizeShapeFactory()
{
	//empty
}

//Factory method for creating shapes based on an input string.
Shape* RandomSizeShapeFactory::createShape(string name)
{
	//create a randomly sized triangle
	if(name == "triangle")
	{
		return new Triangle(getRandomNumber(),
						    getRandomNumber(),
						    0,0);
	}
	//create a randomly sized circle
	else if(name == "circle")
	{
		return new Circle(getRandomNumber(),0,0);
	}
	//create a randomly sized rectangle
	else if(name == "rectangle")
	{
		return new Rectangle(getRandomNumber(),
						    getRandomNumber(),
						    0,0);
	}
	
	//return NULL if we don't recognize the input string...in theory
	//we should also consider throwing an exception here
	return NULL;
}
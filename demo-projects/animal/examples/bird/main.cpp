#include <string>
#include <iostream>
#include "bird.h"

int main(int argc, char const *argv[])
{
	Bird bird("Polly", 2, "Parrot");
	std::cout << bird.getName() << " is a " << bird.getAge() << " year old " << bird.getSpecies() << std::endl;
	return 0;
}

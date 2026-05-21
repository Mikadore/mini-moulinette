#include <stdio.h>
#include "../../../../ex03/ft_point.h"
#include "../../../../ex03/ft_point.h"
#include "../../../utils/constants.h"

void	set_point(t_point *point)
{
	point->x = 42;
	point->y = 21;
}

int	main(void)
{
	t_point	point;

	point.x = 0;
	point.y = 0;
	set_point(&point);
	if (point.x != 42 || point.y != 21)
	{
		printf("    " RED "[KO] set_point did not populate x/y correctly\n" DEFAULT);
		return (1);
	}
	printf("  " GREEN CHECKMARK GREY " t_point structure and fields are valid.\n" DEFAULT);
	return (0);
}

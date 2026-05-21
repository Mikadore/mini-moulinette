#include <stdio.h>
#include "../../../../ex02/ft_abs.h"
#include "../../../utils/constants.h"

static int	g_errors = 0;

static void	report_check(int ok, const char *desc, int got, int expected)
{
	if (!ok)
	{
		g_errors++;
		printf("    " RED "[KO] %s (expected %d, got %d)\n" DEFAULT,
			desc, expected, got);
		return ;
	}
	printf("  " GREEN CHECKMARK GREY " %s\n" DEFAULT, desc);
}

int	main(void)
{
	int	value;

	value = ABS(5);
	report_check(value == 5, "ABS(5) == 5", value, 5);
	value = ABS(-5);
	report_check(value == 5, "ABS(-5) == 5", value, 5);
	value = ABS(0);
	report_check(value == 0, "ABS(0) == 0", value, 0);
	value = ABS(2 - 5);
	report_check(value == 3, "ABS(2 - 5) == 3", value, 3);
	value = ABS(-3) * 2;
	report_check(value == 6, "ABS(-3) * 2 == 6", value, 6);
	value = 10 / ABS(-2);
	report_check(value == 5, "10 / ABS(-2) == 5", value, 5);
	value = ABS(-(7));
	report_check(value == 7, "ABS(-(7)) == 7", value, 7);
	return (g_errors);
}

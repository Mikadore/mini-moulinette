#include <stdio.h>
#include <string.h>
#include "../../../../ex01/ft_boolean.h"
#include "../../../utils/constants.h"

static int	g_errors = 0;

static void	report_result(int ok, const char *desc)
{
	if (!ok)
	{
		g_errors++;
		printf("    " RED "[KO] %s\n" DEFAULT, desc);
		return ;
	}
	printf("  " GREEN CHECKMARK GREY " %s\n" DEFAULT, desc);
}

int	main(void)
{
	t_bool	even_value;
	t_bool	odd_value;

	report_result(TRUE == 1, "TRUE equals 1");
	report_result(FALSE == 0, "FALSE equals 0");
	report_result(SUCCESS == 0, "SUCCESS equals 0");
	report_result(EVEN(0), "EVEN(0) is true");
	report_result(!EVEN(1), "EVEN(1) is false");
	report_result(EVEN(2), "EVEN(2) is true");
	report_result(EVEN(-2), "EVEN(-2) is true");
	report_result(!EVEN(-3), "EVEN(-3) is false");
	report_result(strcmp(EVEN_MSG, "I have an even number of arguments.\n") == 0,
		"EVEN_MSG is exact");
	report_result(strcmp(ODD_MSG, "I have an odd number of arguments.\n") == 0,
		"ODD_MSG is exact");
	even_value = EVEN(42);
	odd_value = EVEN(41);
	report_result(even_value == TRUE, "t_bool stores TRUE result from EVEN");
	report_result(odd_value == FALSE, "t_bool stores FALSE result from EVEN");
	if (g_errors != 0)
		return (g_errors);
	return (SUCCESS);
}

#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include "resources/ft_stock_str.h"
#include "../../../../ex05/ft_show_tab.c"
#include "../../../utils/constants.h"

static int	report_case(int ok, const char *name)
{
	if (!ok)
	{
		printf("    " RED "[KO] %s\n" DEFAULT, name);
		return (1);
	}
	printf("  " GREEN CHECKMARK GREY " %s\n" DEFAULT, name);
	return (0);
}

static int	capture_stdout(struct s_stock_str *input, char *buffer, size_t capacity)
{
	int		pipefd[2];
	int		saved_stdout;
	ssize_t	bytes_read;
	size_t	total;

	if (pipe(pipefd) == -1)
		return (-1);
	saved_stdout = dup(STDOUT_FILENO);
	if (saved_stdout == -1)
	{
		close(pipefd[0]);
		close(pipefd[1]);
		return (-1);
	}
	fflush(stdout);
	if (dup2(pipefd[1], STDOUT_FILENO) == -1)
	{
		close(pipefd[0]);
		close(pipefd[1]);
		close(saved_stdout);
		return (-1);
	}
	close(pipefd[1]);
	ft_show_tab(input);
	fflush(stdout);
	if (dup2(saved_stdout, STDOUT_FILENO) == -1)
	{
		close(pipefd[0]);
		close(saved_stdout);
		return (-1);
	}
	close(saved_stdout);
	total = 0;
	bytes_read = 0;
	while (total + 1 < capacity)
	{
		bytes_read = read(pipefd[0], buffer + total, capacity - total - 1);
		if (bytes_read <= 0)
			break ;
		total += (size_t)bytes_read;
	}
	close(pipefd[0]);
	if (bytes_read < 0)
		return (-1);
	if (total + 1 == capacity)
		return (-2);
	buffer[total] = '\0';
	return ((int)total);
}

static int	run_output_case(
	const char *name,
	struct s_stock_str *input,
	const char *expected
)
{
	char	captured[4096];
	int	capture_status;
	int	errors;

	errors = 0;
	capture_status = capture_stdout(input, captured, sizeof(captured));
	errors += report_case(capture_status >= 0, name);
	if (capture_status < 0)
		return (errors + 1);
	if (strcmp(captured, expected) != 0)
	{
		printf("    " RED "Expected output:\n%s" DEFAULT, expected);
		printf("    " RED "Captured output:\n%s" DEFAULT, captured);
		errors += report_case(0, "output matches expected bytes exactly");
	}
	else
		errors += report_case(1, "output matches expected bytes exactly");
	return (errors);
}

int	main(void)
{
	int				errors;
	struct s_stock_str	single_case[] = {
		{2, "hi", "HI"},
		{0, 0, 0},
	};
	struct s_stock_str	multi_case[] = {
		{0, "", ""},
		{12, "abcdefghijkl", "ABCDEFGHIJKL"},
		{4, "same", "COPY"},
		{0, 0, 0},
		{5, "extra", "EXTRA"},
	};
	const char			single_expected[] = "hi\n2\nHI\n";
	const char			multi_expected[] =
		"\n0\n\n"
		"abcdefghijkl\n12\nABCDEFGHIJKL\n"
		"same\n4\nCOPY\n";

	errors = 0;
	errors += run_output_case("single-entry output", single_case, single_expected);
	errors += run_output_case("multi-entry output and sentinel stop", multi_case,
		multi_expected);
	if (errors != 0)
		return (1);
	return (0);
}

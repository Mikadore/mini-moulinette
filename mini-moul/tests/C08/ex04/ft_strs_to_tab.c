#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ft_stock_str.h"
#include "../../../utils/constants.h"

#define TRACK_CAPACITY 4096

static void		*g_tracked_ptrs[TRACK_CAPACITY];
static size_t	g_tracked_sizes[TRACK_CAPACITY];
static int		g_tracked_count = 0;
static int		g_live_allocs = 0;
static int		g_malloc_calls = 0;
static int		g_fail_on_call = 0;
static int		g_tracking_enabled = 0;

static void	tracker_reset(int fail_on_call, int tracking_enabled)
{
	int	index;

	index = 0;
	while (index < TRACK_CAPACITY)
	{
		g_tracked_ptrs[index] = NULL;
		g_tracked_sizes[index] = 0;
		index++;
	}
	g_tracked_count = 0;
	g_live_allocs = 0;
	g_malloc_calls = 0;
	g_fail_on_call = fail_on_call;
	g_tracking_enabled = tracking_enabled;
}

static int	tracker_find(void *ptr)
{
	int	index;

	index = 0;
	while (index < g_tracked_count)
	{
		if (g_tracked_ptrs[index] == ptr)
			return (index);
		index++;
	}
	return (-1);
}

static int	tracker_is_tracked(void *ptr)
{
	if (!g_tracking_enabled || ptr == NULL)
		return (0);
	return (tracker_find(ptr) >= 0);
}

static size_t	tracker_allocation_size(void *ptr)
{
	int	index;

	if (!g_tracking_enabled || ptr == NULL)
		return (0);
	index = tracker_find(ptr);
	if (index < 0)
		return (0);
	return (g_tracked_sizes[index]);
}

static void	tracker_add(void *ptr, size_t size)
{
	if (!g_tracking_enabled || ptr == NULL)
		return ;
	if (g_tracked_count < TRACK_CAPACITY)
	{
		g_tracked_ptrs[g_tracked_count] = ptr;
		g_tracked_sizes[g_tracked_count] = size;
		g_tracked_count++;
	}
	g_live_allocs++;
}

static void	tracker_remove(void *ptr)
{
	int	index;

	if (!g_tracking_enabled || ptr == NULL)
		return ;
	index = tracker_find(ptr);
	if (index < 0)
		return ;
	g_tracked_ptrs[index] = g_tracked_ptrs[g_tracked_count - 1];
	g_tracked_sizes[index] = g_tracked_sizes[g_tracked_count - 1];
	g_tracked_ptrs[g_tracked_count - 1] = NULL;
	g_tracked_sizes[g_tracked_count - 1] = 0;
	g_tracked_count--;
	if (g_live_allocs > 0)
		g_live_allocs--;
}

static void	tracker_release_all(void)
{
	int	index;

	index = 0;
	while (index < g_tracked_count)
	{
		if (g_tracked_ptrs[index] != NULL)
			free(g_tracked_ptrs[index]);
		g_tracked_ptrs[index] = NULL;
		g_tracked_sizes[index] = 0;
		index++;
	}
	g_tracked_count = 0;
	g_live_allocs = 0;
}

void	*harness_malloc(size_t size)
{
	void	*ptr;

	g_malloc_calls++;
	if (g_fail_on_call > 0 && g_malloc_calls == g_fail_on_call)
		return (NULL);
	ptr = malloc(size);
	tracker_add(ptr, size);
	return (ptr);
}

void	harness_free(void *ptr)
{
	tracker_remove(ptr);
	free(ptr);
}

#define malloc(size) harness_malloc(size)
#define free(ptr) harness_free(ptr)
#include "../../../../ex04/ft_strs_to_tab.c"
#undef malloc
#undef free

static int	report_check(int ok, const char *message)
{
	if (!ok)
	{
		printf("    " RED "[KO] %s\n" DEFAULT, message);
		return (1);
	}
	printf("  " GREEN CHECKMARK GREY " %s\n" DEFAULT, message);
	return (0);
}

static void	free_tracked_student_result(struct s_stock_str *result, int ac)
{
	int	index;

	if (result == NULL)
		return ;
	index = 0;
	while (index < ac)
	{
		if (tracker_is_tracked(result[index].copy))
			harness_free(result[index].copy);
		index++;
	}
	if (tracker_is_tracked(result))
		harness_free(result);
}

static int	test_regular_behavior(void)
{
	int				errors;
	int				index;
	int				expected_size;
	int				copy_is_tracked;
	size_t			array_size;
	char				str0[] = "";
	char				str1[] = "hello";
	char				str2[] = "this is a longer string";
	char				*av[] = {str0, str1, str2};
	struct s_stock_str	*result;
	char				original_char;

	errors = 0;
	tracker_reset(0, 1);
	result = ft_strs_to_tab(3, av);
	errors += report_check(result != NULL,
		"ft_strs_to_tab returns non-NULL for valid input");
	if (result == NULL)
		return (errors + 1);
	array_size = tracker_allocation_size(result);
	errors += report_check(array_size >= sizeof(struct s_stock_str) * 4,
		"result allocates space for ac + 1 entries");
	if (array_size < sizeof(struct s_stock_str) * 4)
	{
		if (tracker_is_tracked(result))
			harness_free(result);
		tracker_release_all();
		return (errors + 1);
	}
	index = 0;
	while (index < 3)
	{
		expected_size = (int)strlen(av[index]);
		errors += report_check(result[index].size == expected_size,
			"size field matches strlen(input)");
		errors += report_check(result[index].str == av[index],
			"str field keeps original pointer identity");
		errors += report_check(result[index].copy != NULL,
			"copy field is allocated");
		if (result[index].copy != NULL)
		{
			copy_is_tracked = tracker_is_tracked(result[index].copy);
			errors += report_check(copy_is_tracked || result[index].copy == av[index],
				"copy pointer is tracked allocation or direct alias");
			errors += report_check(result[index].copy != av[index],
				"copy field is a deep copy, not alias");
			if (copy_is_tracked)
				errors += report_check(strcmp(result[index].copy, av[index]) == 0,
					"copy string content matches input");
		}
		index++;
	}
	errors += report_check(result[3].str == 0,
		"result is sentinel-terminated with .str == 0");
	original_char = av[1][0];
	if (result[1].copy != NULL)
	{
		if (tracker_is_tracked(result[1].copy) || result[1].copy == av[1])
			result[1].copy[0] = 'H';
	}
	errors += report_check(av[1][0] == original_char,
		"mutating copy does not mutate original input string");
	free_tracked_student_result(result, 3);
	errors += report_check(g_live_allocs == 0,
		"regular-path cleanup leaves no tracked live allocations");
	tracker_release_all();
	return (errors);
}

static int	test_ac_zero_behavior(void)
{
	int				errors;
	size_t			array_size;
	char				sample[] = "unused";
	char				*av[] = {sample};
	struct s_stock_str	*result;

	errors = 0;
	tracker_reset(0, 1);
	result = ft_strs_to_tab(0, av);
	errors += report_check(result != NULL,
		"ac == 0 returns a non-NULL allocated sentinel array");
	if (result == NULL)
		return (errors + 1);
	array_size = tracker_allocation_size(result);
	errors += report_check(array_size >= sizeof(struct s_stock_str),
		"ac == 0 allocates at least one struct entry");
	if (array_size >= sizeof(struct s_stock_str))
		errors += report_check(result[0].str == 0,
			"ac == 0 result[0].str is sentinel zero");
	if (tracker_is_tracked(result))
		harness_free(result);
	errors += report_check(g_live_allocs == 0,
		"ac == 0 cleanup leaves no tracked live allocations");
	tracker_release_all();
	return (errors);
}

static int	test_malloc_failures(void)
{
	int				errors;
	int				fail_call;
	int				total_malloc_calls;
	size_t			array_size;
	char				str0[] = "";
	char				str1[] = "hello";
	char				str2[] = "world";
	char				*av[] = {str0, str1, str2};
	char				message[128];
	struct s_stock_str	*result;

	errors = 0;
	tracker_reset(0, 1);
	result = ft_strs_to_tab(3, av);
	errors += report_check(result != NULL,
		"control run with tracking enabled succeeds");
	if (result == NULL)
		return (errors + 1);
	total_malloc_calls = g_malloc_calls;
	array_size = tracker_allocation_size(result);
	if (array_size >= sizeof(struct s_stock_str) * 4)
		free_tracked_student_result(result, 3);
	else if (tracker_is_tracked(result))
		harness_free(result);
	errors += report_check(g_live_allocs == 0,
		"control run frees tracked allocations after cleanup");
	errors += report_check(total_malloc_calls > 0,
		"control run performs at least one malloc call");
	tracker_release_all();
	fail_call = 1;
	while (fail_call <= total_malloc_calls)
	{
		tracker_reset(fail_call, 1);
		result = ft_strs_to_tab(3, av);
		snprintf(message, sizeof(message),
			"failure on malloc call #%d returns NULL", fail_call);
		errors += report_check(result == NULL, message);
		snprintf(message, sizeof(message),
			"failure on malloc call #%d frees all prior allocations", fail_call);
		errors += report_check(g_live_allocs == 0, message);
		tracker_release_all();
		fail_call++;
	}
	return (errors);
}

int	main(void)
{
	int	errors;

	errors = 0;
	errors += test_regular_behavior();
	errors += test_ac_zero_behavior();
	errors += test_malloc_failures();
	if (errors != 0)
		return (1);
	return (0);
}

#include <stdio.h>
#include "../../../../ex00/ft.h"
#include "../../../../ex00/ft.h"
#include "../../../utils/constants.h"

static void (*g_putchar)(char) = ft_putchar;
static void (*g_swap)(int *, int *) = ft_swap;
static void (*g_putstr)(char *) = ft_putstr;
static int (*g_strlen)(char *) = ft_strlen;
static int (*g_strcmp)(char *, char *) = ft_strcmp;

void	ft_putchar(char c)
{
	(void)c;
}

void	ft_swap(int *a, int *b)
{
	int	tmp;

	tmp = *a;
	*a = *b;
	*b = tmp;
}

void	ft_putstr(char *str)
{
	(void)str;
}

int	ft_strlen(char *str)
{
	int	len;

	len = 0;
	while (str && str[len])
		len++;
	return (len);
}

int	ft_strcmp(char *s1, char *s2)
{
	while (*s1 && *s1 == *s2)
	{
		s1++;
		s2++;
	}
	return ((unsigned char)*s1 - (unsigned char)*s2);
}

int	main(void)
{
	int		a;
	int		b;
	char	text[] = "abc";

	a = 1;
	b = 2;
	g_putchar('x');
	g_swap(&a, &b);
	g_putstr(text);
	if (g_strlen(text) != 3)
		return (1);
	if (g_strcmp("abc", "abc") != 0)
		return (1);
	if (a != 2 || b != 1)
		return (1);
	printf("  " GREEN CHECKMARK GREY " Header declarations and signatures are valid.\n" DEFAULT);
	return (0);
}

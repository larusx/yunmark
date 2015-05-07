/**
 * Created by larus on 15/2/9.
 */
angular.module('myApp').directive('taginput', function () {
    return {
        restrict: 'E',
        template: '<input name="{{name}}" class="tagsinput tagsinput-primary" ng-value="values" />',
        replace: true,
        scope: {
            tags: '=',
            name: '@',
            id: '@'
        },
        link: function ($scope, element, attrs) {
            $scope.name = attrs.name;
            $scope.id = attrs.id;

            $scope.$watch('tags', function (value) {
                if (!value)
                    value = [];
                $scope.values = value;
                element.tagsInput(value.toString());

            });

            element.tagsInput({
                onAddTag: function (value) {
                    $scope.values.push(value);
                    $scope.$apply(function () {
                        $scope.tags = $scope.values;
                    });
                }
            });
        },
        controller: function ($scope) {
        }
    }

});
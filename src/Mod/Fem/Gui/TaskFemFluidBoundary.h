/***************************************************************************
 *   Copyright (c) 2013 Jan Rheinländer <jrheinlaender@users.sourceforge.net>        *
 *                                                                         *
 *   This file is part of the FreeCAD CAx development system.              *
 *                                                                         *
 *   This library is free software; you can redistribute it and/or         *
 *   modify it under the terms of the GNU Library General Public           *
 *   License as published by the Free Software Foundation; either          *
 *   version 2 of the License, or (at your option) any later version.      *
 *                                                                         *
 *   This library  is distributed in the hope that it will be useful,      *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 *   GNU Library General Public License for more details.                  *
 *                                                                         *
 *   You should have received a copy of the GNU Library General Public     *
 *   License along with this library; see the file COPYING.LIB. If not,    *
 *   write to the Free Software Foundation, Inc., 59 Temple Place,         *
 *   Suite 330, Boston, MA  02111-1307, USA                                *
 *                                                                         *
 ***************************************************************************/


#ifndef GUI_TASKVIEW_TaskFemFluidBoundary_H
#define GUI_TASKVIEW_TaskFemFluidBoundary_H

#include <Gui/TaskView/TaskView.h>
#include <Gui/Selection.h>
#include <Gui/TaskView/TaskDialog.h>

#include "TaskFemConstraint.h"
#include "ViewProviderFemFluidBoundary.h"

class Ui_TaskFemFluidBoundary;

namespace App {
class Property;
}

namespace Gui {
class ViewProvider;
}

namespace FemGui {

class TaskFemFluidBoundary : public TaskFemConstraint
{
    Q_OBJECT

public:
    TaskFemFluidBoundary(ViewProviderFemFluidBoundary *ConstraintView,QWidget *parent = 0);
    virtual ~TaskFemFluidBoundary();

    const char* getBoundaryType(void) const;
    const char* getSubtype(void) const;
    double getBoundaryValue(void) const;
    virtual const std::string getReferences() const;
    const std::string getDirectionName(void) const;
    const std::string getDirectionObject(void) const;
    bool getReverse(void) const;

private Q_SLOTS:
    void onBoundaryTypeChanged(const char*);
    void onSubtypeChanged(const char*);
    void onBoundaryValueChanged(double);
    void onReferenceDeleted(void);
    void onButtonDirection(const bool pressed = true);
    void onCheckReverse(bool);

protected:
    virtual void changeEvent(QEvent *e);

private:
    virtual void onSelectionChanged(const Gui::SelectionChanges& msg);
    void updateSelectionUI();
    void updateBoundaryTypeUI();
    void updateSubtypeUI();

private:
    Ui_TaskFemFluidBoundary* ui;
};

/// simulation dialog for the TaskView
class TaskDlgFemFluidBoundary : public TaskDlgFemConstraint
{
    Q_OBJECT

public:
    TaskDlgFemFluidBoundary(ViewProviderFemFluidBoundary *ConstraintView);

    /// is called by the framework if the dialog is accepted (Ok)
    virtual void open();
    virtual bool accept();
    virtual bool reject();

};

} //namespace FemGui

#endif // GUI_TASKVIEW_TaskFemFluidBoundary_H
